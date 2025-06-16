"""
Unit tests for Task Lifecycle Management in A2A Protocol v0.2.1
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from tekton.a2a.task import (
    Task, TaskState, TaskPriority, TaskUpdate, TaskManager
)
from tekton.a2a.errors import TaskStateError, TaskNotFoundError


class TestTask:
    """Test Task functionality"""
    
    def test_create_task(self):
        """Test creating a task"""
        task = Task.create(
            name="Test Task",
            created_by="test-agent",
            description="A test task",
            input_data={"key": "value"},
            priority=TaskPriority.HIGH
        )
        
        assert task.id.startswith("task-")
        assert task.name == "Test Task"
        assert task.created_by == "test-agent"
        assert task.description == "A test task"
        assert task.input_data == {"key": "value"}
        assert task.priority == TaskPriority.HIGH
        assert task.state == TaskState.PENDING
        assert task.progress == 0.0
        assert isinstance(task.created_at, datetime)
    
    def test_task_state_transitions_valid(self):
        """Test valid task state transitions"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # Pending -> Running
        assert task.can_transition_to(TaskState.RUNNING)
        task.transition_to(TaskState.RUNNING)
        assert task.state == TaskState.RUNNING
        assert task.started_at is not None
        
        # Running -> Completed
        assert task.can_transition_to(TaskState.COMPLETED)
        task.transition_to(TaskState.COMPLETED)
        assert task.state == TaskState.COMPLETED
        assert task.completed_at is not None
        assert task.progress == 1.0
    
    def test_task_state_transitions_invalid(self):
        """Test invalid task state transitions"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # Cannot go from PENDING to COMPLETED directly
        assert not task.can_transition_to(TaskState.COMPLETED)
        
        with pytest.raises(TaskStateError):
            task.transition_to(TaskState.COMPLETED)
    
    def test_task_state_transitions_with_message(self):
        """Test task state transitions with messages"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        task.transition_to(TaskState.RUNNING, "Starting task execution")
        
        # Check update was recorded
        assert len(task.updates) == 1
        update = task.updates[0]
        assert update.state == TaskState.RUNNING
        assert update.message == "Starting task execution"
        assert isinstance(update.timestamp, datetime)
    
    def test_task_pause_resume(self):
        """Test pausing and resuming a task"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # Start task
        task.transition_to(TaskState.RUNNING)
        
        # Pause task
        assert task.can_transition_to(TaskState.PAUSED)
        task.transition_to(TaskState.PAUSED, "Pausing for user input")
        assert task.state == TaskState.PAUSED
        
        # Resume task
        assert task.can_transition_to(TaskState.RUNNING)
        task.transition_to(TaskState.RUNNING, "Resuming execution")
        assert task.state == TaskState.RUNNING
    
    def test_task_cancellation(self):
        """Test task cancellation"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # Can cancel from PENDING
        assert task.can_transition_to(TaskState.CANCELLED)
        task.transition_to(TaskState.CANCELLED, "User cancelled")
        assert task.state == TaskState.CANCELLED
        assert task.completed_at is not None
    
    def test_task_failure(self):
        """Test task failure"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # Start task
        task.transition_to(TaskState.RUNNING)
        
        # Fail task
        assert task.can_transition_to(TaskState.FAILED)
        task.transition_to(TaskState.FAILED, "Error occurred")
        assert task.state == TaskState.FAILED
        assert task.completed_at is not None
    
    def test_terminal_states(self):
        """Test that terminal states cannot transition"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # Complete the task
        task.transition_to(TaskState.RUNNING)
        task.transition_to(TaskState.COMPLETED)
        
        # Cannot transition from completed
        assert task.is_terminal()
        for state in TaskState:
            assert not task.can_transition_to(state)
    
    def test_update_progress(self):
        """Test updating task progress"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # Update progress
        task.update_progress(0.25, "25% complete")
        assert task.progress == 0.25
        
        task.update_progress(0.75, "75% complete")
        assert task.progress == 0.75
        
        # Check updates
        assert len(task.updates) == 2
        assert task.updates[0].progress == 0.25
        assert task.updates[0].message == "25% complete"
        assert task.updates[1].progress == 0.75
        assert task.updates[1].message == "75% complete"
    
    def test_update_progress_invalid(self):
        """Test invalid progress values"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        with pytest.raises(ValueError):
            task.update_progress(-0.1)
        
        with pytest.raises(ValueError):
            task.update_progress(1.1)
    
    def test_add_update(self):
        """Test adding general updates"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        task.add_update("Processing step 1", {"step": 1, "status": "ok"})
        task.add_update("Processing step 2", {"step": 2, "status": "ok"})
        
        assert len(task.updates) == 2
        assert task.updates[0].message == "Processing step 1"
        assert task.updates[0].data == {"step": 1, "status": "ok"}
    
    def test_set_output(self):
        """Test setting task output"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        output_data = {"result": "success", "value": 42}
        task.set_output(output_data)
        
        assert task.output_data == output_data
    
    def test_set_error(self):
        """Test setting task error"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        error_data = {"error": "Division by zero", "line": 10}
        task.set_error(error_data)
        
        assert task.error_data == error_data
    
    def test_task_duration(self):
        """Test calculating task duration"""
        task = Task.create(name="Test Task", created_by="test-agent")
        
        # No duration before starting
        assert task.duration() is None
        
        # Start task
        task.transition_to(TaskState.RUNNING)
        task.started_at = datetime.now(timezone.utc) - timedelta(seconds=30)
        
        # Still no duration until completed
        assert task.duration() is None
        
        # Complete task
        task.transition_to(TaskState.COMPLETED)
        task.completed_at = datetime.now(timezone.utc)
        
        # Now has duration
        duration = task.duration()
        assert duration is not None
        assert 29 <= duration <= 31  # Allow for small timing variations


class TestTaskManager:
    """Test Task Manager functionality"""
    
    def test_create_task(self):
        """Test creating a task through manager"""
        manager = TaskManager()
        
        task = manager.create_task(
            name="Test Task",
            created_by="test-agent",
            description="A test task",
            input_data={"key": "value"}
        )
        
        assert task.name == "Test Task"
        assert task.created_by == "test-agent"
        assert task.id in manager._tasks
    
    def test_get_task(self):
        """Test getting a task by ID"""
        manager = TaskManager()
        
        task = manager.create_task(name="Test Task", created_by="test-agent")
        retrieved = manager.get_task(task.id)
        
        assert retrieved == task
    
    def test_get_nonexistent_task(self):
        """Test getting a non-existent task raises error"""
        manager = TaskManager()
        
        with pytest.raises(TaskNotFoundError):
            manager.get_task("nonexistent-id")
    
    def test_list_tasks_no_filter(self):
        """Test listing all tasks"""
        manager = TaskManager()
        
        # Create multiple tasks
        task1 = manager.create_task(name="Task 1", created_by="agent-1")
        task2 = manager.create_task(name="Task 2", created_by="agent-2")
        task3 = manager.create_task(name="Task 3", created_by="agent-1")
        
        all_tasks = manager.list_tasks()
        assert len(all_tasks) == 3
        assert task1 in all_tasks
        assert task2 in all_tasks
        assert task3 in all_tasks
    
    def test_list_tasks_by_agent(self):
        """Test listing tasks filtered by agent"""
        manager = TaskManager()
        
        # Create tasks for different agents
        task1 = manager.create_task(name="Task 1", created_by="agent-1")
        task2 = manager.create_task(name="Task 2", created_by="agent-2")
        task3 = manager.create_task(name="Task 3", created_by="agent-1")
        
        # Assign tasks
        manager.assign_task(task1.id, "agent-1")
        manager.assign_task(task2.id, "agent-2")
        manager.assign_task(task3.id, "agent-1")
        
        # Filter by agent
        agent1_tasks = manager.list_tasks(agent_id="agent-1")
        assert len(agent1_tasks) == 2
        assert task1 in agent1_tasks
        assert task3 in agent1_tasks
    
    def test_list_tasks_by_state(self):
        """Test listing tasks filtered by state"""
        manager = TaskManager()
        
        # Create tasks in different states
        task1 = manager.create_task(name="Task 1", created_by="agent-1")
        task2 = manager.create_task(name="Task 2", created_by="agent-1")
        task3 = manager.create_task(name="Task 3", created_by="agent-1")
        
        # Update states
        manager.update_task_state(task2.id, TaskState.RUNNING)
        manager.update_task_state(task3.id, TaskState.RUNNING)
        manager.complete_task(task3.id)
        
        # Filter by state
        pending_tasks = manager.list_tasks(state=TaskState.PENDING)
        assert len(pending_tasks) == 1
        assert task1 in pending_tasks
        
        running_tasks = manager.list_tasks(state=TaskState.RUNNING)
        assert len(running_tasks) == 1
        assert task2 in running_tasks
        
        completed_tasks = manager.list_tasks(state=TaskState.COMPLETED)
        assert len(completed_tasks) == 1
        assert task3 in completed_tasks
    
    def test_list_tasks_by_created_by(self):
        """Test listing tasks filtered by creator"""
        manager = TaskManager()
        
        # Create tasks by different creators
        task1 = manager.create_task(name="Task 1", created_by="agent-1")
        task2 = manager.create_task(name="Task 2", created_by="agent-2")
        task3 = manager.create_task(name="Task 3", created_by="agent-1")
        
        # Filter by creator
        agent1_created = manager.list_tasks(created_by="agent-1")
        assert len(agent1_created) == 2
        assert task1 in agent1_created
        assert task3 in agent1_created
    
    def test_assign_task(self):
        """Test assigning a task to an agent"""
        manager = TaskManager()
        
        task = manager.create_task(name="Test Task", created_by="creator")
        assert task.agent_id is None
        
        # Assign task
        assigned = manager.assign_task(task.id, "agent-123")
        assert assigned.agent_id == "agent-123"
        
        # Check update was recorded
        assert any("Assigned to agent agent-123" in update.message 
                  for update in task.updates if update.message)
    
    def test_update_task_state(self):
        """Test updating task state through manager"""
        manager = TaskManager()
        
        task = manager.create_task(name="Test Task", created_by="agent-1")
        
        # Update state
        updated = manager.update_task_state(
            task.id, 
            TaskState.RUNNING, 
            "Starting execution"
        )
        
        assert updated.state == TaskState.RUNNING
        assert updated.started_at is not None
    
    def test_update_task_progress(self):
        """Test updating task progress through manager"""
        manager = TaskManager()
        
        task = manager.create_task(name="Test Task", created_by="agent-1")
        
        # Update progress
        updated = manager.update_task_progress(
            task.id,
            0.5,
            "Halfway done"
        )
        
        assert updated.progress == 0.5
    
    def test_complete_task(self):
        """Test completing a task"""
        manager = TaskManager()
        
        task = manager.create_task(name="Test Task", created_by="agent-1")
        manager.update_task_state(task.id, TaskState.RUNNING)
        
        # Complete with output
        output_data = {"result": "success", "count": 10}
        completed = manager.complete_task(
            task.id,
            output_data,
            "Task completed successfully"
        )
        
        assert completed.state == TaskState.COMPLETED
        assert completed.output_data == output_data
        assert completed.progress == 1.0
    
    def test_fail_task(self):
        """Test failing a task"""
        manager = TaskManager()
        
        task = manager.create_task(name="Test Task", created_by="agent-1")
        manager.update_task_state(task.id, TaskState.RUNNING)
        
        # Fail with error
        error_data = {"error": "Network timeout", "code": "E001"}
        failed = manager.fail_task(
            task.id,
            error_data,
            "Network connection failed"
        )
        
        assert failed.state == TaskState.FAILED
        assert failed.error_data == error_data
    
    def test_cancel_task(self):
        """Test cancelling a task"""
        manager = TaskManager()
        
        task = manager.create_task(name="Test Task", created_by="agent-1")
        
        # Cancel task
        cancelled = manager.cancel_task(task.id, "User requested cancellation")
        
        assert cancelled.state == TaskState.CANCELLED
        assert cancelled.completed_at is not None
    
    def test_cleanup_completed(self):
        """Test cleaning up completed tasks"""
        manager = TaskManager()
        
        # Create tasks in various states
        task1 = manager.create_task(name="Task 1", created_by="agent-1")
        task2 = manager.create_task(name="Task 2", created_by="agent-1")
        task3 = manager.create_task(name="Task 3", created_by="agent-1")
        task4 = manager.create_task(name="Task 4", created_by="agent-1")
        
        # Complete some tasks
        manager.update_task_state(task2.id, TaskState.RUNNING)
        manager.complete_task(task2.id)
        
        manager.update_task_state(task3.id, TaskState.RUNNING)
        manager.fail_task(task3.id, {"error": "test"})
        
        manager.cancel_task(task4.id)
        
        # Set completion times
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        task2.completed_at = old_time
        task3.completed_at = old_time
        
        # Cleanup old completed tasks
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        removed_ids = manager.cleanup_completed(before=cutoff)
        
        assert len(removed_ids) == 2
        assert task2.id in removed_ids
        assert task3.id in removed_ids
        
        # Check remaining tasks
        remaining = manager.list_tasks()
        assert len(remaining) == 2
        assert task1 in remaining  # Still pending
        assert task4 in remaining  # Recently cancelled