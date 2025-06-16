#!/usr/bin/env python3
"""Test MCP tool with manual subtask creation"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metis.core.task_manager import TaskManager
from metis.models.task import Task
from metis.models.subtask import Subtask
from metis.models.complexity import ComplexityScore
from metis.models.enums import TaskStatus, Priority
from metis.core.mcp.tools import get_task_manager
from uuid import uuid4

async def test_manual_subtasks():
    """Test the task manager with manual subtask creation"""
    print("Testing Metis task management with manual subtasks...")
    print("-" * 50)
    
    # Get the shared task manager instance
    task_manager = get_task_manager()
    
    # Create a test task
    test_task = Task(
        title="Build a REST API for user management",
        description="Create a complete REST API with endpoints for user registration, login, profile management, and password reset. Include JWT authentication and proper error handling.",
        status=TaskStatus.PENDING,
        priority=Priority.HIGH
    )
    
    # Add the task
    created_task = task_manager.storage.create_task(test_task)
    print(f"Created test task: {created_task.id}")
    print(f"Title: {created_task.title}")
    
    # Manually create subtasks
    subtasks_data = [
        {
            "title": "Design Authentication Schema",
            "description": "Design database schema for users, sessions, and auth tokens",
            "estimated_hours": 2,
            "complexity": 3
        },
        {
            "title": "Implement User Model and Database",
            "description": "Create user model with fields for email, password hash, profile data",
            "estimated_hours": 3,
            "complexity": 5
        },
        {
            "title": "Create Registration Endpoint",
            "description": "Implement POST /register endpoint with validation and password hashing",
            "estimated_hours": 4,
            "complexity": 5
        },
        {
            "title": "Implement Login with JWT",
            "description": "Create POST /login endpoint that returns JWT tokens",
            "estimated_hours": 4,
            "complexity": 6
        }
    ]
    
    print("\nAdding subtasks manually...")
    for idx, subtask_data in enumerate(subtasks_data):
        # Create complexity score
        complexity = ComplexityScore(
            technical_complexity=subtask_data["complexity"],
            time_complexity=subtask_data["estimated_hours"],
            dependency_complexity=0,
            overall_score=subtask_data["complexity"]
        )
        
        # Create subtask
        subtask = Subtask(
            id=str(uuid4()),
            parent_task_id=created_task.id,
            title=subtask_data["title"],
            description=subtask_data["description"],
            estimated_hours=subtask_data["estimated_hours"],
            order=idx + 1,
            complexity=complexity,
            status=TaskStatus.PENDING
        )
        
        # Add to task
        created_task.add_subtask(subtask)
        print(f"  Added: {subtask.title} ({subtask.estimated_hours}h)")
    
    # Update task in storage
    task_manager.storage.update_task(created_task.id, {"subtasks": created_task.subtasks})
    
    # Verify subtasks were added
    print("\nVerifying subtasks...")
    verified_task = task_manager.storage.get_task(created_task.id)
    print(f"Task has {len(verified_task.subtasks)} subtasks")
    
    total_hours = sum(st.estimated_hours for st in verified_task.subtasks)
    print(f"Total estimated hours: {total_hours}")
    
    # Test the API endpoint simulation
    print("\n" + "-" * 50)
    print("Simulating API endpoint: /api/v1/tasks/{task_id}/decompose")
    print(f"Task ID: {created_task.id}")
    print("Response:")
    response = {
        "success": True,
        "task_id": created_task.id,
        "subtasks": [
            {
                "id": st.id,
                "title": st.title,
                "description": st.description,
                "estimated_hours": st.estimated_hours,
                "complexity": st.complexity.overall_score if st.complexity else 0,
                "order": st.order,
                "status": st.status
            }
            for st in verified_task.subtasks
        ],
        "total_hours": total_hours,
        "subtask_count": len(verified_task.subtasks)
    }
    
    import json
    print(json.dumps(response, indent=2))
    
    # Cleanup
    task_manager.storage.delete_task(created_task.id)
    print(f"\nCleaned up test task: {created_task.id}")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_manual_subtasks())
    sys.exit(0 if success else 1)