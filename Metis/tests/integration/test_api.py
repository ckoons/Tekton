"""
Integration tests for Metis API

This module contains integration tests for the Metis API endpoints,
testing the complete request-response cycle.
"""

import pytest
from fastapi.testclient import TestClient
import json
from uuid import uuid4

from metis.api.app import app
from metis.models.enums import TaskStatus, Priority


# Create test client
client = TestClient(app)


class TestTaskAPI:
    """Integration tests for task API endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Metis"
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test the health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Metis"
    
    def test_create_task(self):
        """Test creating a task via API."""
        task_data = {
            "title": "API Test Task",
            "description": "This task tests the API",
            "status": TaskStatus.PENDING.value,
            "priority": Priority.MEDIUM.value,
            "tags": ["api", "test"]
        }
        
        response = client.post("/api/v1/tasks", json=task_data)
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["priority"] == task_data["priority"]
        assert data["tags"] == task_data["tags"]
        assert "id" in data
        
        # Save task ID for later tests
        task_id = data["id"]
        return task_id
    
    def test_get_task(self):
        """Test getting a task via API."""
        # Create a task first
        task_id = self.test_create_task()
        
        # Get the task
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["task"]["id"] == task_id
        assert data["task"]["title"] == "API Test Task"
    
    def test_list_tasks(self):
        """Test listing tasks via API."""
        # Create some tasks first
        self.test_create_task()  # API Test Task
        
        # Create another task with different properties
        task_data = {
            "title": "Another API Test Task",
            "description": "This is another API test task",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": Priority.HIGH.value,
            "tags": ["api", "important"]
        }
        response = client.post("/api/v1/tasks", json=task_data)
        assert response.status_code == 201
        
        # List all tasks
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["total"] >= 2  # At least the two tasks we created
        
        # Test filtering by status
        response = client.get(f"/api/v1/tasks?status={TaskStatus.IN_PROGRESS.value}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["tasks"]) >= 1
        assert all(task["status"] == TaskStatus.IN_PROGRESS.value for task in data["tasks"])
        
        # Test filtering by priority
        response = client.get(f"/api/v1/tasks?priority={Priority.HIGH.value}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["tasks"]) >= 1
        assert all(task["priority"] == Priority.HIGH.value for task in data["tasks"])
        
        # Test filtering by tag
        response = client.get("/api/v1/tasks?tag=important")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["tasks"]) >= 1
        assert all("important" in task["tags"] for task in data["tasks"])
        
        # Test search
        response = client.get("/api/v1/tasks?search=Another")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["tasks"]) >= 1
        assert any("Another" in task["title"] for task in data["tasks"])
    
    def test_update_task(self):
        """Test updating a task via API."""
        # Create a task first
        task_id = self.test_create_task()
        
        # Update the task
        update_data = {
            "title": "Updated API Test Task",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": Priority.HIGH.value
        }
        
        response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == task_id
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]
        
        # Verify update
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["task"]["title"] == update_data["title"]
        assert data["task"]["status"] == update_data["status"]
        assert data["task"]["priority"] == update_data["priority"]
    
    def test_add_subtask(self):
        """Test adding a subtask via API."""
        # Create a task first
        task_id = self.test_create_task()
        
        # Add subtask
        subtask_data = {
            "title": "API Test Subtask",
            "description": "This is a test subtask",
            "status": TaskStatus.PENDING.value
        }
        
        response = client.post(f"/api/v1/tasks/{task_id}/subtasks", json=subtask_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == task_id
        assert len(data["subtasks"]) == 1
        assert data["subtasks"][0]["title"] == subtask_data["title"]
        
        # Save subtask ID for later tests
        subtask_id = data["subtasks"][0]["id"]
        
        # Update subtask
        update_data = {
            "title": "Updated API Test Subtask",
            "status": TaskStatus.IN_PROGRESS.value
        }
        
        response = client.put(f"/api/v1/tasks/{task_id}/subtasks/{subtask_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == task_id
        assert data["subtasks"][0]["id"] == subtask_id
        assert data["subtasks"][0]["title"] == update_data["title"]
        assert data["subtasks"][0]["status"] == update_data["status"]
        
        # Delete subtask
        response = client.delete(f"/api/v1/tasks/{task_id}/subtasks/{subtask_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == task_id
        assert len(data["subtasks"]) == 0
    
    def test_dependencies(self):
        """Test dependency operations via API."""
        # Create two tasks
        task1_data = {
            "title": "Dependency Source Task",
            "description": "This is the source task"
        }
        response = client.post("/api/v1/tasks", json=task1_data)
        assert response.status_code == 201
        task1_id = response.json()["id"]
        
        task2_data = {
            "title": "Dependency Target Task",
            "description": "This is the target task"
        }
        response = client.post("/api/v1/tasks", json=task2_data)
        assert response.status_code == 201
        task2_id = response.json()["id"]
        
        # Create dependency
        dependency_data = {
            "source_task_id": task1_id,
            "target_task_id": task2_id,
            "dependency_type": "blocks",
            "description": "Source task blocks target task"
        }
        
        response = client.post("/api/v1/dependencies", json=dependency_data)
        assert response.status_code == 201
        data = response.json()
        
        assert data["source_task_id"] == task1_id
        assert data["target_task_id"] == task2_id
        assert data["dependency_type"] == dependency_data["dependency_type"]
        
        # Save dependency ID
        dependency_id = data["id"]
        
        # Verify dependency added to target task
        response = client.get(f"/api/v1/tasks/{task2_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert task1_id in data["task"]["dependencies"]
        
        # List dependencies
        response = client.get("/api/v1/dependencies")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["dependencies"]) >= 1
        
        # List dependencies for a specific task
        response = client.get(f"/api/v1/tasks/{task2_id}/dependencies")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["dependencies"]) >= 1
        
        # Update dependency
        update_data = {
            "dependency_type": "depends_on",
            "description": "Target task depends on source task"
        }
        
        response = client.put(f"/api/v1/dependencies/{dependency_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == dependency_id
        assert data["dependency_type"] == update_data["dependency_type"]
        assert data["description"] == update_data["description"]
        
        # Delete dependency
        response = client.delete(f"/api/v1/dependencies/{dependency_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        
        # Verify dependency removed from target task
        response = client.get(f"/api/v1/tasks/{task2_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert task1_id not in data["task"]["dependencies"]
    
    def test_delete_task(self):
        """Test deleting a task via API."""
        # Create a task first
        task_id = self.test_create_task()
        
        # Delete the task
        response = client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        
        # Verify deletion
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 404