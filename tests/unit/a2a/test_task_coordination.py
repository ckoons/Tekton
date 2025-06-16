"""
Unit tests for A2A task coordination features
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from tekton.a2a.task import Task, TaskState, TaskPriority, TaskManager
from tekton.a2a.task_coordination import (
    TaskCoordinator, CoordinationPattern, DependencyType,
    TaskWorkflow, TaskDependency, ConditionalRule
)
from tekton.a2a.errors import InvalidRequestError


class TestTaskDependency:
    """Test task dependency functionality"""
    
    def test_finish_to_start_dependency(self):
        """Test finish-to-start dependency"""
        dep = TaskDependency(
            predecessor_id="task-1",
            successor_id="task-2",
            dependency_type=DependencyType.FINISH_TO_START
        )
        
        # Create mock tasks
        tasks = {
            "task-1": Mock(state=TaskState.RUNNING),
            "task-2": Mock(state=TaskState.PENDING)
        }
        
        # Not satisfied when predecessor is running
        assert not dep.is_satisfied(tasks)
        
        # Satisfied when predecessor is completed
        tasks["task-1"].state = TaskState.COMPLETED
        assert dep.is_satisfied(tasks)
    
    def test_start_to_start_dependency(self):
        """Test start-to-start dependency"""
        dep = TaskDependency(
            predecessor_id="task-1",
            successor_id="task-2",
            dependency_type=DependencyType.START_TO_START
        )
        
        tasks = {
            "task-1": Mock(state=TaskState.PENDING),
            "task-2": Mock(state=TaskState.PENDING)
        }
        
        # Not satisfied when predecessor hasn't started
        assert not dep.is_satisfied(tasks)
        
        # Satisfied when predecessor is running
        tasks["task-1"].state = TaskState.RUNNING
        assert dep.is_satisfied(tasks)
        
        # Also satisfied when predecessor is completed
        tasks["task-1"].state = TaskState.COMPLETED
        assert dep.is_satisfied(tasks)


class TestConditionalRule:
    """Test conditional rule evaluation"""
    
    def test_simple_equality_condition(self):
        """Test simple equality conditions"""
        rule = ConditionalRule(
            condition="status == 'success'",
            true_task_id="task-success",
            false_task_id="task-failure"
        )
        
        # Test true case
        assert rule.evaluate({"status": "success"})
        
        # Test false case
        assert not rule.evaluate({"status": "failure"})
    
    def test_numeric_comparison(self):
        """Test numeric comparisons"""
        rule_gt = ConditionalRule(condition="score > 80")
        assert rule_gt.evaluate({"score": 90})
        assert not rule_gt.evaluate({"score": 70})
        
        rule_lt = ConditionalRule(condition="count < 10")
        assert rule_lt.evaluate({"count": 5})
        assert not rule_lt.evaluate({"count": 15})
    
    def test_boolean_condition(self):
        """Test boolean conditions"""
        rule = ConditionalRule(condition="is_complete")
        assert rule.evaluate({"is_complete": True})
        assert not rule.evaluate({"is_complete": False})
        assert not rule.evaluate({})  # Missing variable


class TestTaskWorkflow:
    """Test TaskWorkflow model"""
    
    def test_workflow_creation(self):
        """Test creating a workflow"""
        workflow = TaskWorkflow.create(
            name="Test Workflow",
            created_by="agent-123",
            pattern=CoordinationPattern.SEQUENTIAL
        )
        
        assert workflow.name == "Test Workflow"
        assert workflow.created_by == "agent-123"
        assert workflow.pattern == CoordinationPattern.SEQUENTIAL
        assert workflow.state == TaskState.PENDING
        assert workflow.id.startswith("workflow-")
    
    def test_add_task_to_workflow(self):
        """Test adding tasks to workflow"""
        workflow = TaskWorkflow.create("Test", "agent-123")
        
        workflow.add_task("step-1", "task-abc")
        workflow.add_task("step-2", "task-def")
        
        assert len(workflow.tasks) == 2
        assert workflow.tasks["step-1"] == "task-abc"
        assert workflow.tasks["step-2"] == "task-def"
    
    def test_add_dependency(self):
        """Test adding dependencies"""
        workflow = TaskWorkflow.create("Test", "agent-123")
        
        workflow.add_task("step-1", "task-1")
        workflow.add_task("step-2", "task-2")
        
        workflow.add_dependency("task-1", "task-2")
        
        assert len(workflow.dependencies) == 1
        assert workflow.dependencies[0].predecessor_id == "task-1"
        assert workflow.dependencies[0].successor_id == "task-2"
    
    def test_get_ready_tasks(self):
        """Test getting tasks ready to execute"""
        workflow = TaskWorkflow.create("Test", "agent-123")
        
        workflow.add_task("step-1", "task-1")
        workflow.add_task("step-2", "task-2")
        workflow.add_task("step-3", "task-3")
        
        workflow.add_dependency("task-1", "task-2")
        workflow.add_dependency("task-2", "task-3")
        
        # Mock task states
        task_states = {
            "task-1": Mock(state=TaskState.PENDING),
            "task-2": Mock(state=TaskState.PENDING),
            "task-3": Mock(state=TaskState.PENDING)
        }
        
        # Only task-1 should be ready (no dependencies)
        ready = workflow.get_ready_tasks(task_states)
        assert ready == ["task-1"]
        
        # After task-1 completes, task-2 should be ready
        task_states["task-1"].state = TaskState.COMPLETED
        ready = workflow.get_ready_tasks(task_states)
        assert ready == ["task-2"]
    
    def test_workflow_completion_check(self):
        """Test checking if workflow is complete"""
        workflow = TaskWorkflow.create("Test", "agent-123")
        
        workflow.add_task("step-1", "task-1")
        workflow.add_task("step-2", "task-2")
        
        # Create mocks with is_terminal method
        task1 = Mock(state=TaskState.COMPLETED)
        task1.is_terminal.return_value = True
        
        task2 = Mock(state=TaskState.RUNNING)
        task2.is_terminal.return_value = False
        
        task_states = {
            "task-1": task1,
            "task-2": task2
        }
        
        # Not complete when tasks are still running
        assert not workflow.is_complete(task_states)
        
        # Complete when all tasks are terminal
        task2.state = TaskState.COMPLETED
        task2.is_terminal.return_value = True
        assert workflow.is_complete(task_states)


class TestTaskCoordinator:
    """Test TaskCoordinator functionality"""
    
    @pytest.fixture
    def task_manager(self):
        """Create a mock task manager"""
        manager = TaskManager()
        # Mock the event callback to avoid issues
        manager._event_callbacks = []
        return manager
    
    @pytest.fixture
    def coordinator(self, task_manager):
        """Create a task coordinator"""
        return TaskCoordinator(task_manager)
    
    @pytest.mark.asyncio
    async def test_create_workflow(self, coordinator):
        """Test creating a workflow"""
        workflow = await coordinator.create_workflow(
            name="Test Workflow",
            created_by="agent-123",
            pattern=CoordinationPattern.PARALLEL,
            max_parallel=3
        )
        
        assert workflow.name == "Test Workflow"
        assert workflow.created_by == "agent-123"
        assert workflow.pattern == CoordinationPattern.PARALLEL
        assert workflow.max_parallel == 3
        assert workflow.id in coordinator.workflows
    
    @pytest.mark.asyncio
    async def test_create_sequential_workflow(self, coordinator):
        """Test creating a sequential workflow"""
        task_defs = [
            {"name": "Task 1", "description": "First task"},
            {"name": "Task 2", "description": "Second task"},
            {"name": "Task 3", "description": "Third task"}
        ]
        
        workflow = await coordinator.create_sequential_workflow(
            name="Sequential Test",
            created_by="agent-123",
            task_definitions=task_defs
        )
        
        assert workflow.pattern == CoordinationPattern.SEQUENTIAL
        assert len(workflow.tasks) == 3
        assert len(workflow.dependencies) == 2  # 1->2, 2->3
        
        # Check dependencies are set up correctly
        deps = sorted(workflow.dependencies, key=lambda d: d.successor_id)
        assert deps[0].dependency_type == DependencyType.FINISH_TO_START
    
    @pytest.mark.asyncio
    async def test_create_parallel_workflow(self, coordinator):
        """Test creating a parallel workflow"""
        task_defs = [
            {"name": "Parallel 1"},
            {"name": "Parallel 2"},
            {"name": "Parallel 3"}
        ]
        
        workflow = await coordinator.create_parallel_workflow(
            name="Parallel Test",
            created_by="agent-123",
            task_definitions=task_defs,
            max_parallel=2
        )
        
        assert workflow.pattern == CoordinationPattern.PARALLEL
        assert workflow.max_parallel == 2
        assert len(workflow.tasks) == 3
        assert len(workflow.dependencies) == 0  # No dependencies in parallel
    
    @pytest.mark.asyncio
    async def test_create_pipeline_workflow(self, coordinator):
        """Test creating a pipeline workflow"""
        stages = [
            {"name": "Extract", "description": "Extract data"},
            {"name": "Transform", "description": "Transform data"},
            {"name": "Load", "description": "Load data"}
        ]
        
        workflow = await coordinator.create_pipeline_workflow(
            name="ETL Pipeline",
            created_by="agent-123",
            task_definitions=stages
        )
        
        assert workflow.pattern == CoordinationPattern.PIPELINE
        assert len(workflow.tasks) == 3
        assert len(workflow.dependencies) == 2
        
        # Check pipeline metadata is set
        task_ids = list(workflow.tasks.values())
        for i in range(1, len(task_ids)):
            task = coordinator.task_manager.get_task(task_ids[i])
            assert "pipeline_input_from" in task.metadata
    
    @pytest.mark.asyncio
    async def test_create_fanout_workflow(self, coordinator):
        """Test creating a fan-out workflow"""
        source = {"name": "Distribute Work"}
        targets = [
            {"name": "Worker 1"},
            {"name": "Worker 2"},
            {"name": "Worker 3"}
        ]
        
        workflow = await coordinator.create_fanout_workflow(
            name="Fan-out Test",
            created_by="agent-123",
            source_task_def=source,
            target_task_defs=targets
        )
        
        assert workflow.pattern == CoordinationPattern.FANOUT
        assert len(workflow.tasks) == 4  # 1 source + 3 targets
        assert len(workflow.dependencies) == 3  # source -> each target
    
    @pytest.mark.asyncio
    async def test_start_workflow(self, coordinator):
        """Test starting a workflow"""
        # Create a simple workflow
        workflow = await coordinator.create_workflow(
            name="Test",
            created_by="agent-123"
        )
        
        # Add a task
        task = coordinator.task_manager.create_task(
            name="Test Task",
            created_by="agent-123"
        )
        workflow.add_task("task-1", task.id)
        
        # Start workflow
        await coordinator.start_workflow(workflow.id)
        
        assert workflow.state == TaskState.RUNNING
        assert workflow.started_at is not None
        assert workflow.id in coordinator._running_workflows
    
    @pytest.mark.asyncio
    async def test_cancel_workflow(self, coordinator):
        """Test cancelling a workflow"""
        # Create and start a workflow
        workflow = await coordinator.create_workflow(
            name="Test",
            created_by="agent-123"
        )
        
        # Add tasks
        task1 = coordinator.task_manager.create_task("Task 1", "agent-123")
        task2 = coordinator.task_manager.create_task("Task 2", "agent-123")
        workflow.add_task("task-1", task1.id)
        workflow.add_task("task-2", task2.id)
        
        await coordinator.start_workflow(workflow.id)
        
        # Cancel workflow
        await coordinator.cancel_workflow(workflow.id, "Test cancellation")
        
        assert workflow.state == TaskState.CANCELLED
        assert workflow.completed_at is not None
        assert workflow.id not in coordinator._running_workflows
    
    @pytest.mark.asyncio
    async def test_workflow_not_found(self, coordinator):
        """Test operations on non-existent workflow"""
        with pytest.raises(InvalidRequestError):
            await coordinator.start_workflow("fake-workflow-id")
        
        with pytest.raises(InvalidRequestError):
            await coordinator.cancel_workflow("fake-workflow-id")
    
    @pytest.mark.asyncio
    async def test_list_workflows(self, coordinator):
        """Test listing workflows"""
        # Create multiple workflows
        w1 = await coordinator.create_workflow("Workflow 1", "agent-123")
        w2 = await coordinator.create_workflow("Workflow 2", "agent-456")
        w3 = await coordinator.create_workflow("Workflow 3", "agent-123")
        
        # Start one workflow
        await coordinator.start_workflow(w1.id)
        
        # List all workflows
        all_workflows = await coordinator.list_workflows()
        assert len(all_workflows) == 3
        
        # List by creator
        agent_workflows = await coordinator.list_workflows(created_by="agent-123")
        assert len(agent_workflows) == 2
        
        # List by state
        running_workflows = await coordinator.list_workflows(state=TaskState.RUNNING)
        assert len(running_workflows) == 1
        assert running_workflows[0].id == w1.id