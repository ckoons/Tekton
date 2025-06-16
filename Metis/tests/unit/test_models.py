"""
Unit tests for Metis models

This module contains tests for the data models used in Metis,
including Task, Dependency, Subtask, and ComplexityScore.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from metis.models.task import Task
from metis.models.dependency import Dependency, DependencyManager
from metis.models.subtask import Subtask, SubtaskTemplate
from metis.models.requirement import RequirementRef
from metis.models.complexity import ComplexityFactor, ComplexityScore, ComplexityTemplate
from metis.models.enums import TaskStatus, Priority, ComplexityLevel


class TestTaskModel:
    """Tests for the Task model."""
    
    def test_task_creation(self):
        """Test creating a Task with default values."""
        task = Task(
            title="Test Task",
            description="This is a test task"
        )
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "This is a test task"
        assert task.status == TaskStatus.PENDING.value
        assert task.priority == Priority.MEDIUM.value
        assert task.dependencies == []
        assert task.subtasks == []
        assert task.requirement_refs == []
        assert task.created_at is not None
        assert task.updated_at is not None
    
    def test_task_creation_with_values(self):
        """Test creating a Task with custom values."""
        task = Task(
            id="task-123",
            title="Custom Task",
            description="This is a custom task",
            status=TaskStatus.IN_PROGRESS.value,
            priority=Priority.HIGH.value,
            dependencies=["task-456"],
            tags=["important", "urgent"],
            assignee="user1"
        )
        
        assert task.id == "task-123"
        assert task.title == "Custom Task"
        assert task.description == "This is a custom task"
        assert task.status == TaskStatus.IN_PROGRESS.value
        assert task.priority == Priority.HIGH.value
        assert task.dependencies == ["task-456"]
        assert task.tags == ["important", "urgent"]
        assert task.assignee == "user1"
    
    def test_task_update(self):
        """Test updating a Task."""
        task = Task(
            title="Test Task",
            description="This is a test task"
        )
        
        # Save the original updated_at time
        original_updated_at = task.updated_at
        
        # Wait a moment to ensure updated_at changes
        import time
        time.sleep(0.001)
        
        # Update the task
        updates = {
            "title": "Updated Task",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": Priority.HIGH.value
        }
        task.update(updates)
        
        assert task.title == "Updated Task"
        assert task.status == TaskStatus.IN_PROGRESS.value
        assert task.priority == Priority.HIGH.value
        assert task.updated_at > original_updated_at
    
    def test_task_update_status(self):
        """Test updating a Task's status."""
        task = Task(
            title="Test Task",
            description="This is a test task"
        )
        
        # Valid transition
        success = task.update_status(TaskStatus.IN_PROGRESS.value)
        assert success
        assert task.status == TaskStatus.IN_PROGRESS.value
        
        # Invalid transition
        with pytest.raises(ValueError):
            task.update_status("invalid_status")
    
    def test_task_dependency_management(self):
        """Test adding and removing dependencies."""
        task = Task(
            title="Test Task",
            description="This is a test task"
        )
        
        # Add dependency
        success = task.add_dependency("task-456")
        assert success
        assert "task-456" in task.dependencies
        
        # Add duplicate dependency
        success = task.add_dependency("task-456")
        assert not success
        
        # Remove dependency
        success = task.remove_dependency("task-456")
        assert success
        assert "task-456" not in task.dependencies
        
        # Remove non-existent dependency
        success = task.remove_dependency("task-789")
        assert not success
    
    def test_task_subtask_management(self):
        """Test adding, updating, and removing subtasks."""
        task = Task(
            title="Test Task",
            description="This is a test task"
        )
        
        # Create subtask
        subtask = Subtask(
            title="Test Subtask",
            description="This is a test subtask"
        )
        
        # Add subtask
        task.add_subtask(subtask)
        assert len(task.subtasks) == 1
        assert task.subtasks[0].title == "Test Subtask"
        
        # Update subtask
        subtask_id = task.subtasks[0].id
        success = task.update_subtask(subtask_id, {"title": "Updated Subtask"})
        assert success
        assert task.subtasks[0].title == "Updated Subtask"
        
        # Remove subtask
        success = task.remove_subtask(subtask_id)
        assert success
        assert len(task.subtasks) == 0
        
        # Remove non-existent subtask
        success = task.remove_subtask("non-existent-id")
        assert not success
    
    def test_task_progress(self):
        """Test calculating task progress."""
        task = Task(
            title="Test Task",
            description="This is a test task"
        )
        
        # No subtasks, various statuses
        assert task.get_progress() == 0.0
        
        task.status = TaskStatus.IN_PROGRESS.value
        assert task.get_progress() == 50.0
        
        task.status = TaskStatus.REVIEW.value
        assert task.get_progress() == 90.0
        
        task.status = TaskStatus.DONE.value
        assert task.get_progress() == 100.0
        
        # With subtasks
        task.status = TaskStatus.IN_PROGRESS.value
        
        # Add subtasks with varying statuses
        subtask1 = Subtask(title="Subtask 1", status=TaskStatus.DONE.value)
        subtask2 = Subtask(title="Subtask 2", status=TaskStatus.IN_PROGRESS.value)
        subtask3 = Subtask(title="Subtask 3", status=TaskStatus.PENDING.value)
        
        task.add_subtask(subtask1)
        task.add_subtask(subtask2)
        task.add_subtask(subtask3)
        
        # Only 1 of 3 subtasks is done, so progress should be ~33.33%
        expected = 100.0 / 3  # = 33.33%
        assert abs(task.get_progress() - expected) < 0.001  # Check with tolerance


class TestSubtaskModel:
    """Tests for the Subtask model."""
    
    def test_subtask_creation(self):
        """Test creating a Subtask with default values."""
        subtask = Subtask(
            title="Test Subtask"
        )
        
        assert subtask.id is not None
        assert subtask.title == "Test Subtask"
        assert subtask.description is None
        assert subtask.status == TaskStatus.PENDING.value
        assert subtask.order == 0
        assert subtask.created_at is not None
        assert subtask.updated_at is not None
    
    def test_subtask_update(self):
        """Test updating a Subtask."""
        subtask = Subtask(
            title="Test Subtask"
        )
        
        # Save the original updated_at time
        original_updated_at = subtask.updated_at
        
        # Wait a moment to ensure updated_at changes
        import time
        time.sleep(0.001)
        
        # Update the subtask
        updates = {
            "title": "Updated Subtask",
            "description": "Updated description",
            "status": TaskStatus.IN_PROGRESS.value,
            "order": 1
        }
        subtask.update(updates)
        
        assert subtask.title == "Updated Subtask"
        assert subtask.description == "Updated description"
        assert subtask.status == TaskStatus.IN_PROGRESS.value
        assert subtask.order == 1
        assert subtask.updated_at > original_updated_at
    
    def test_subtask_status_validation(self):
        """Test validating status transitions for Subtask."""
        subtask = Subtask(
            title="Test Subtask"
        )
        
        # Valid transition
        subtask.update({"status": TaskStatus.IN_PROGRESS.value})
        assert subtask.status == TaskStatus.IN_PROGRESS.value
        
        # Invalid transition
        with pytest.raises(ValueError):
            subtask.update({"status": "invalid_status"})
    
    def test_subtask_template(self):
        """Test creating subtasks from a template."""
        template = SubtaskTemplate(
            name="Test Template",
            description="Template for testing subtasks",
            subtasks=[
                {"title": "Subtask 1", "description": "Description 1"},
                {"title": "Subtask 2", "description": "Description 2"},
                {"title": "Subtask 3", "description": "Description 3"}
            ]
        )
        
        # Create subtasks from template
        subtasks = template.create_subtasks()
        
        assert len(subtasks) == 3
        assert subtasks[0].title == "Subtask 1"
        assert subtasks[0].description == "Description 1"
        assert subtasks[0].order == 0
        
        assert subtasks[1].title == "Subtask 2"
        assert subtasks[1].description == "Description 2"
        assert subtasks[1].order == 1
        
        assert subtasks[2].title == "Subtask 3"
        assert subtasks[2].description == "Description 3"
        assert subtasks[2].order == 2


class TestComplexityModel:
    """Tests for the complexity models."""
    
    def test_complexity_factor(self):
        """Test creating and using ComplexityFactor."""
        factor = ComplexityFactor(
            name="Technical Difficulty",
            description="Technical complexity of the task",
            weight=1.5,
            score=4
        )
        
        assert factor.id is not None
        assert factor.name == "Technical Difficulty"
        assert factor.description == "Technical complexity of the task"
        assert factor.weight == 1.5
        assert factor.score == 4
        assert factor.notes is None
        
        # Test weighted score calculation
        assert factor.calculate_weighted_score() == 6.0  # 4 * 1.5
    
    def test_complexity_score(self):
        """Test creating and updating ComplexityScore."""
        # Create an empty score
        score = ComplexityScore()
        
        assert score.id is not None
        assert score.factors == []
        assert score.overall_score == 3.0  # Default
        assert score.level == ComplexityLevel.MODERATE.value
        
        # Add factors
        factor1 = ComplexityFactor(
            name="Technical Difficulty",
            description="Technical complexity of the task",
            weight=1.5,
            score=4
        )
        
        factor2 = ComplexityFactor(
            name="Scope Size",
            description="Size of the task",
            weight=1.0,
            score=2
        )
        
        score.add_factor(factor1)
        score.add_factor(factor2)
        
        assert len(score.factors) == 2
        
        # Calculate weighted average: (4*1.5 + 2*1.0) / (1.5 + 1.0) = 8.0 / 2.5 = 3.2
        # Rounded to nearest integer for level: 3 = MODERATE
        assert score.overall_score == 3.2
        assert score.level == ComplexityLevel.MODERATE.value
        
        # Update factor
        score.update_factor(factor1.id, {"score": 5})
        
        # Recalculated: (5*1.5 + 2*1.0) / (1.5 + 1.0) = 9.5 / 2.5 = 3.8
        # Rounded to nearest integer for level: 4 = COMPLEX
        assert score.overall_score == 3.8
        assert score.level == ComplexityLevel.COMPLEX.value
        
        # Remove factor
        score.remove_factor(factor1.id)
        
        assert len(score.factors) == 1
        assert score.overall_score == 2.0
        assert score.level == ComplexityLevel.SIMPLE.value
    
    def test_complexity_template(self):
        """Test creating complexity scores from templates."""
        template = ComplexityTemplate(
            name="Feature Template",
            description="Template for feature complexity",
            factors=[
                ComplexityFactor(
                    name="Technical Difficulty",
                    description="Technical complexity",
                    weight=1.5,
                    score=4
                ),
                ComplexityFactor(
                    name="Scope Size",
                    description="Size of the feature",
                    weight=1.0,
                    score=3
                )
            ]
        )
        
        # Create score from template
        score = template.create_score()
        
        assert score.id is not None
        assert len(score.factors) == 2
        assert score.overall_score == 3.6  # (4*1.5 + 3*1.0) / (1.5 + 1.0) = 9.0 / 2.5 = 3.6
        assert score.level == ComplexityLevel.COMPLEX.value


class TestDependencyModel:
    """Tests for the Dependency model."""
    
    def test_dependency_creation(self):
        """Test creating a Dependency."""
        dependency = Dependency(
            source_task_id="task-123",
            target_task_id="task-456",
            dependency_type="depends_on",
            description="Task 123 depends on Task 456"
        )
        
        assert dependency.id is not None
        assert dependency.source_task_id == "task-123"
        assert dependency.target_task_id == "task-456"
        assert dependency.dependency_type == "depends_on"
        assert dependency.description == "Task 123 depends on Task 456"
        assert dependency.created_at is not None
        assert dependency.updated_at is not None
    
    def test_dependency_update(self):
        """Test updating a Dependency."""
        dependency = Dependency(
            source_task_id="task-123",
            target_task_id="task-456"
        )
        
        # Save the original updated_at time
        original_updated_at = dependency.updated_at
        
        # Wait a moment to ensure updated_at changes
        import time
        time.sleep(0.001)
        
        # Update the dependency
        updates = {
            "dependency_type": "blocks",
            "description": "Task 456 blocks Task 123"
        }
        dependency.update(updates)
        
        assert dependency.dependency_type == "blocks"
        assert dependency.description == "Task 456 blocks Task 123"
        assert dependency.updated_at > original_updated_at
    
    def test_dependency_manager_validation(self):
        """Test dependency validation."""
        # Create some dependencies
        dep1 = Dependency(source_task_id="task-1", target_task_id="task-2")
        dep2 = Dependency(source_task_id="task-2", target_task_id="task-3")
        dependencies = [dep1, dep2]
        
        # Valid dependency
        is_valid = DependencyManager.validate_new_dependency(
            dependencies, "task-3", "task-4"
        )
        assert is_valid
        
        # Circular dependency (would create cycle: 1->2->3->1)
        is_valid = DependencyManager.validate_new_dependency(
            dependencies, "task-3", "task-1"
        )
        assert not is_valid
        
        # Self-dependency (not allowed)
        is_valid = DependencyManager.validate_new_dependency(
            dependencies, "task-1", "task-1"
        )
        assert not is_valid
    
    def test_dependency_manager_blocking_tasks(self):
        """Test getting blocking tasks."""
        # Create some dependencies
        dep1 = Dependency(source_task_id="task-1", target_task_id="task-3", dependency_type="blocks")
        dep2 = Dependency(source_task_id="task-2", target_task_id="task-3", dependency_type="depends_on")
        dep3 = Dependency(source_task_id="task-3", target_task_id="task-4", dependency_type="related_to")
        dependencies = [dep1, dep2, dep3]
        
        # Get blocking tasks for task-3
        blocking_tasks = DependencyManager.get_blocking_tasks(dependencies, "task-3")
        assert len(blocking_tasks) == 2
        assert "task-1" in blocking_tasks
        assert "task-2" in blocking_tasks
        
        # Get blocking tasks for task-4 (related_to doesn't count as blocking)
        blocking_tasks = DependencyManager.get_blocking_tasks(dependencies, "task-4")
        assert len(blocking_tasks) == 0


class TestRequirementRefModel:
    """Tests for the RequirementRef model."""
    
    def test_requirement_ref_creation(self):
        """Test creating a RequirementRef."""
        req_ref = RequirementRef(
            requirement_id="req-123",
            source="telos",
            requirement_type="functional",
            title="Test Requirement",
            relationship="implements",
            description="This requirement is implemented by the task"
        )
        
        assert req_ref.id is not None
        assert req_ref.requirement_id == "req-123"
        assert req_ref.source == "telos"
        assert req_ref.requirement_type == "functional"
        assert req_ref.title == "Test Requirement"
        assert req_ref.relationship == "implements"
        assert req_ref.description == "This requirement is implemented by the task"
        assert req_ref.created_at is not None
        assert req_ref.updated_at is not None
    
    def test_requirement_ref_update(self):
        """Test updating a RequirementRef."""
        req_ref = RequirementRef(
            requirement_id="req-123",
            source="telos",
            requirement_type="functional",
            title="Test Requirement"
        )
        
        # Save the original updated_at time
        original_updated_at = req_ref.updated_at
        
        # Wait a moment to ensure updated_at changes
        import time
        time.sleep(0.001)
        
        # Update the requirement reference
        updates = {
            "title": "Updated Requirement",
            "relationship": "related_to",
            "description": "This task is related to the requirement"
        }
        req_ref.update(updates)
        
        assert req_ref.title == "Updated Requirement"
        assert req_ref.relationship == "related_to"
        assert req_ref.description == "This task is related to the requirement"
        assert req_ref.updated_at > original_updated_at