#!/usr/bin/env python3
"""Test MCP decompose_task tool"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metis.core.task_manager import TaskManager
from metis.models.task import Task
from metis.models.enums import TaskStatus, Priority
from metis.core.mcp.tools import decompose_task, analyze_task_complexity, get_task_manager

async def test_mcp_tool():
    """Test the MCP decompose_task tool"""
    print("Testing Metis MCP decompose_task tool...")
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
    
    # Add the task (use storage directly since it's sync)
    created_task = task_manager.storage.create_task(test_task)
    print(f"Created test task: {created_task.id}")
    print(f"Title: {created_task.title}")
    
    # Verify it's in storage
    verify_task = task_manager.storage.get_task(created_task.id)
    print(f"Verified task exists: {verify_task is not None}")
    print()
    
    # Test decompose_task tool
    print("Testing decompose_task MCP tool...")
    result = await decompose_task(
        task_id=created_task.id,
        depth=2,
        max_subtasks=6,
        auto_create=True
    )
    
    if result.get("success"):
        print("✓ Task decomposition successful!")
        print(f"  Model: {result.get('model', 'unknown')}")
        print(f"  Provider: {result.get('provider', 'unknown')}")
        print(f"  Subtasks created: {len(result.get('subtasks', []))}")
        print()
        
        # Get the updated task to see subtasks
        updated_task = task_manager.storage.get_task(created_task.id)
        if updated_task and updated_task.subtasks:
            print("  Created subtasks:")
            for i, subtask in enumerate(updated_task.subtasks, 1):
                print(f"    {i}. {subtask.title}")
                print(f"       Hours: {subtask.estimated_hours}")
                print(f"       Complexity: {subtask.complexity.overall_score if subtask.complexity else 'N/A'}")
    else:
        print("✗ Task decomposition failed!")
        print(f"  Error: {result.get('error')}")
        return False
    
    print("\n" + "-" * 50)
    
    # Test complexity analysis
    print("Testing analyze_task_complexity MCP tool...")
    complexity_result = await analyze_task_complexity(
        task_id=created_task.id,
        include_subtasks=True
    )
    
    if complexity_result.get("success"):
        print("✓ Complexity analysis successful!")
        analysis = complexity_result.get("analysis", {})
        print(f"  Complexity Score: {analysis.get('complexity_score', 'N/A')}")
        print(f"  Complexity Level: {analysis.get('complexity_level', 'N/A')}")
        if 'explanation' in analysis:
            print(f"  Explanation: {analysis['explanation'][:100]}...")
    else:
        print("✗ Complexity analysis failed!")
        print(f"  Error: {complexity_result.get('error')}")
    
    # Cleanup
    task_manager.storage.delete_task(created_task.id)
    print(f"\nCleaned up test task: {created_task.id}")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_tool())
    sys.exit(0 if success else 1)