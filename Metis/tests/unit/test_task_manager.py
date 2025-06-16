"""
Unit tests for Metis task manager

This module contains tests for the TaskManager class, which provides
the core business logic for managing tasks in Metis.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from metis.core.task_manager import TaskManager
from metis.core.storage import InMemoryStorage
from metis.models.task import Task
from metis.models.dependency import Dependency
from metis.models.subtask import Subtask
from metis.models.requirement import RequirementRef
from metis.models.enums import TaskStatus, Priority


@pytest.fixture
def task_manager():
    """Create a TaskManager instance for testing."""
    return TaskManager(InMemoryStorage())


class TestTaskManager:
    """Tests for the TaskManager class."""
    
    @pytest.mark.asyncio
    async def test_create_task(self, task_manager):
        """Test creating a task."""
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "status": TaskStatus.PENDING.value,
            "priority": Priority.MEDIUM.value
        }
        
        task = await task_manager.create_task(task_data)
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "This is a test task"
        assert task.status == TaskStatus.PENDING.value
        assert task.priority == Priority.MEDIUM.value
    
    @pytest.mark.asyncio
    async def test_get_task(self, task_manager):
        """Test getting a task by ID."""
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "This is a test task"
        }
        task = await task_manager.create_task(task_data)
        
        # Get the task
        retrieved_task = await task_manager.get_task(task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == task.title
        
        # Try to get a non-existent task
        non_existent_task = await task_manager.get_task("non-existent-id")
        assert non_existent_task is None
    
    @pytest.mark.asyncio
    async def test_update_task(self, task_manager):
        """Test updating a task."""
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "This is a test task"
        }
        task = await task_manager.create_task(task_data)
        
        # Update the task
        updates = {
            "title": "Updated Task",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": Priority.HIGH.value
        }
        updated_task = await task_manager.update_task(task.id, updates)
        
        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.status == TaskStatus.IN_PROGRESS.value
        assert updated_task.priority == Priority.HIGH.value
        
        # Try to update a non-existent task
        non_existent_task = await task_manager.update_task("non-existent-id", updates)
        assert non_existent_task is None
    
    @pytest.mark.asyncio
    async def test_delete_task(self, task_manager):
        """Test deleting a task."""
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "This is a test task"
        }
        task = await task_manager.create_task(task_data)
        
        # Delete the task
        deleted = await task_manager.delete_task(task.id)
        assert deleted
        
        # Verify task is deleted
        retrieved_task = await task_manager.get_task(task.id)
        assert retrieved_task is None
        
        # Try to delete a non-existent task
        deleted = await task_manager.delete_task("non-existent-id")
        assert not deleted
    
    @pytest.mark.asyncio
    async def test_list_tasks(self, task_manager):
        """Test listing tasks with filtering."""
        # Create some tasks
        await task_manager.create_task({
            "title": "Task 1",
            "description": "Description 1",
            "status": TaskStatus.PENDING.value,
            "priority": Priority.HIGH.value,
            "tags": ["important"]
        })
        
        await task_manager.create_task({
            "title": "Task 2",
            "description": "Description 2",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": Priority.MEDIUM.value,
            "tags": ["urgent"]
        })
        
        await task_manager.create_task({
            "title": "Task 3",
            "description": "Description 3",
            "status": TaskStatus.PENDING.value,
            "priority": Priority.LOW.value,
            "assignee": "user1"
        })
        
        # List all tasks
        tasks, total = await task_manager.list_tasks()
        assert total == 3
        assert len(tasks) == 3
        
        # Filter by status
        tasks, total = await task_manager.list_tasks(status=TaskStatus.PENDING.value)
        assert total == 2
        assert len(tasks) == 2
        assert all(task.status == TaskStatus.PENDING.value for task in tasks)
        
        # Filter by priority
        tasks, total = await task_manager.list_tasks(priority=Priority.HIGH.value)
        assert total == 1
        assert len(tasks) == 1
        assert tasks[0].priority == Priority.HIGH.value
        
        # Filter by assignee
        tasks, total = await task_manager.list_tasks(assignee="user1")
        assert total == 1
        assert len(tasks) == 1
        assert tasks[0].assignee == "user1"
        
        # Filter by tag
        tasks, total = await task_manager.list_tasks(tag="important")
        assert total == 1
        assert len(tasks) == 1
        assert "important" in tasks[0].tags
        
        # Search by title/description
        tasks, total = await task_manager.list_tasks(search="Description 2")
        assert total == 1
        assert len(tasks) == 1
        assert tasks[0].description == "Description 2"
        
        # Pagination
        tasks, total = await task_manager.list_tasks(page=1, page_size=2)
        assert total == 3
        assert len(tasks) == 2
        
        tasks, total = await task_manager.list_tasks(page=2, page_size=2)
        assert total == 3
        assert len(tasks) == 1
    
    @pytest.mark.asyncio
    async def test_subtask_operations(self, task_manager):
        """Test subtask operations."""
        # Create a task
        task_data = {
            "title": "Parent Task",
            "description": "This is a parent task"
        }
        task = await task_manager.create_task(task_data)
        
        # Add subtask
        subtask_data = {
            "title": "Subtask 1",
            "description": "This is a subtask"
        }
        subtask = await task_manager.add_subtask(task.id, subtask_data)
        
        assert subtask is not None
        assert subtask.title == "Subtask 1"
        
        # Verify subtask was added to task
        updated_task = await task_manager.get_task(task.id)
        assert len(updated_task.subtasks) == 1
        assert updated_task.subtasks[0].title == "Subtask 1"
        
        # Update subtask
        subtask_id = updated_task.subtasks[0].id
        subtask_updates = {
            "title": "Updated Subtask",
            "status": TaskStatus.IN_PROGRESS.value
        }
        updated_subtask = await task_manager.update_subtask(task.id, subtask_id, subtask_updates)
        
        assert updated_subtask is not None
        assert updated_subtask.title == "Updated Subtask"
        assert updated_subtask.status == TaskStatus.IN_PROGRESS.value
        
        # Verify subtask was updated in task
        updated_task = await task_manager.get_task(task.id)
        assert updated_task.subtasks[0].title == "Updated Subtask"
        assert updated_task.subtasks[0].status == TaskStatus.IN_PROGRESS.value
        
        # Remove subtask
        removed = await task_manager.remove_subtask(task.id, subtask_id)
        assert removed
        
        # Verify subtask was removed from task
        updated_task = await task_manager.get_task(task.id)
        assert len(updated_task.subtasks) == 0
    
    @pytest.mark.asyncio
    async def test_requirement_ref_operations(self, task_manager):
        """Test requirement reference operations."""
        # Create a task
        task_data = {
            "title": "Task with Requirements",
            "description": "This task has requirement references"
        }
        task = await task_manager.create_task(task_data)
        
        # Add requirement reference
        req_ref_data = {
            "requirement_id": "req-123",
            "source": "telos",
            "requirement_type": "functional",
            "title": "Test Requirement",
            "relationship": "implements"
        }
        req_ref = await task_manager.add_requirement_ref(task.id, req_ref_data)
        
        assert req_ref is not None
        assert req_ref.requirement_id == "req-123"
        
        # Verify requirement reference was added to task
        updated_task = await task_manager.get_task(task.id)
        assert len(updated_task.requirement_refs) == 1
        assert updated_task.requirement_refs[0].requirement_id == "req-123"
        
        # Update requirement reference
        ref_id = updated_task.requirement_refs[0].id
        ref_updates = {
            "title": "Updated Requirement",
            "relationship": "related_to"
        }
        updated_ref = await task_manager.update_requirement_ref(task.id, ref_id, ref_updates)
        
        assert updated_ref is not None
        assert updated_ref.title == "Updated Requirement"
        assert updated_ref.relationship == "related_to"
        
        # Verify requirement reference was updated in task
        updated_task = await task_manager.get_task(task.id)
        assert updated_task.requirement_refs[0].title == "Updated Requirement"
        assert updated_task.requirement_refs[0].relationship == "related_to"
        
        # Remove requirement reference
        removed = await task_manager.remove_requirement_ref(task.id, ref_id)
        assert removed
        
        # Verify requirement reference was removed from task
        updated_task = await task_manager.get_task(task.id)
        assert len(updated_task.requirement_refs) == 0
    
    @pytest.mark.asyncio
    async def test_dependency_operations(self, task_manager):
        """Test dependency operations."""
        # Create two tasks
        task1 = await task_manager.create_task({
            "title": "Task 1",
            "description": "This is task 1"
        })
        
        task2 = await task_manager.create_task({
            "title": "Task 2",
            "description": "This is task 2"
        })
        
        # Create dependency
        dependency_data = {
            "source_task_id": task1.id,
            "target_task_id": task2.id,
            "dependency_type": "blocks",
            "description": "Task 1 blocks Task 2"
        }
        dependency = await task_manager.create_dependency(dependency_data)
        
        assert dependency is not None
        assert dependency.source_task_id == task1.id
        assert dependency.target_task_id == task2.id
        
        # Verify dependency was added to target task
        updated_task2 = await task_manager.get_task(task2.id)
        assert task1.id in updated_task2.dependencies
        
        # Get dependency
        retrieved_dependency = await task_manager.get_dependency(dependency.id)
        assert retrieved_dependency is not None
        assert retrieved_dependency.id == dependency.id
        
        # Update dependency
        dependency_updates = {
            "dependency_type": "depends_on",
            "description": "Task 2 depends on Task 1"
        }
        updated_dependency = await task_manager.update_dependency(dependency.id, dependency_updates)
        
        assert updated_dependency is not None
        assert updated_dependency.dependency_type == "depends_on"
        assert updated_dependency.description == "Task 2 depends on Task 1"
        
        # List dependencies
        dependencies = await task_manager.list_dependencies()
        assert len(dependencies) == 1
        
        dependencies = await task_manager.list_dependencies(task_id=task1.id)
        assert len(dependencies) == 1
        
        dependencies = await task_manager.list_dependencies(dependency_type="depends_on")
        assert len(dependencies) == 1
        
        # Delete dependency
        deleted = await task_manager.delete_dependency(dependency.id)
        assert deleted
        
        # Verify dependency was removed
        dependencies = await task_manager.list_dependencies()
        assert len(dependencies) == 0
        
        # Verify dependency was removed from target task
        updated_task2 = await task_manager.get_task(task2.id)
        assert task1.id not in updated_task2.dependencies
    
    @pytest.mark.asyncio
    async def test_bulk_operations(self, task_manager):
        """Test bulk task operations."""
        # Bulk create tasks
        tasks_data = [
            {
                "title": "Bulk Task 1",
                "description": "This is bulk task 1"
            },
            {
                "title": "Bulk Task 2",
                "description": "This is bulk task 2"
            },
            {
                "title": "Bulk Task 3",
                "description": "This is bulk task 3"
            }
        ]
        
        tasks = await task_manager.bulk_create_tasks(tasks_data)
        assert len(tasks) == 3
        
        # Get task IDs
        task_ids = [task.id for task in tasks]
        
        # Bulk update tasks
        updates_map = {
            task_ids[0]: {"status": TaskStatus.IN_PROGRESS.value},
            task_ids[1]: {"priority": Priority.HIGH.value},
            task_ids[2]: {"title": "Updated Bulk Task 3"}
        }
        
        updated_tasks = await task_manager.bulk_update_tasks(updates_map)
        assert len(updated_tasks) == 3
        
        # Verify updates were applied
        assert updated_tasks[task_ids[0]].status == TaskStatus.IN_PROGRESS.value
        assert updated_tasks[task_ids[1]].priority == Priority.HIGH.value
        assert updated_tasks[task_ids[2]].title == "Updated Bulk Task 3"
    
    @pytest.mark.asyncio
    async def test_event_handlers(self, task_manager):
        """Test event handling."""
        # Create event tracking variables
        events = []
        
        # Define event handler
        def event_handler(event_type, data):
            events.append((event_type, data))
        
        # Register event handler
        task_manager.register_event_handler("task_created", event_handler)
        task_manager.register_event_handler("task_updated", event_handler)
        task_manager.register_event_handler("task_deleted", event_handler)
        
        # Create task
        task = await task_manager.create_task({
            "title": "Event Test Task",
            "description": "This task tests events"
        })
        
        # Verify task_created event was fired
        assert len(events) == 1
        assert events[0][0] == "task_created"
        assert events[0][1].id == task.id
        
        # Update task
        await task_manager.update_task(task.id, {"title": "Updated Event Test Task"})
        
        # Verify task_updated event was fired
        assert len(events) == 2
        assert events[1][0] == "task_updated"
        assert events[1][1].id == task.id
        
        # Delete task
        await task_manager.delete_task(task.id)
        
        # Verify task_deleted event was fired
        assert len(events) == 3
        assert events[2][0] == "task_deleted"
        assert events[2][1]["id"] == task.id
        
        # Unregister event handler
        task_manager.unregister_event_handler("task_created", event_handler)
        
        # Create another task
        another_task = await task_manager.create_task({
            "title": "Another Test Task",
            "description": "This is another test task"
        })
        
        # Verify no task_created event was fired (handler was unregistered)
        assert len(events) == 3
        
        # But task_updated event handler is still registered
        await task_manager.update_task(another_task.id, {"title": "Updated Another Test Task"})
        assert len(events) == 4
        assert events[3][0] == "task_updated"