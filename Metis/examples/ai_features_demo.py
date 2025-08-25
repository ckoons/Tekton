#!/usr/bin/env python3
"""
Demo script showing Metis CI features

This script demonstrates:
1. Creating a task
2. Using CI to decompose it into subtasks
3. Analyzing task complexity with AI
4. Getting CI suggestions for task ordering
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from metis.core.task_manager import TaskManager
from metis.models.task import Task
from metis.models.enums import TaskStatus, Priority
from metis.core.mcp.tools import (
    get_task_manager,
    decompose_task,
    analyze_task_complexity,
    suggest_task_order,
    generate_subtasks
)

async def demo_ai_features():
    """Demonstrate Metis CI features"""
    print("=== Metis CI Features Demo ===")
    print()
    
    # Get shared task manager
    task_manager = get_task_manager()
    
    # Create some test tasks
    tasks = [
        Task(
            title="Design database schema",
            description="Design the database schema for the application including users, products, and orders",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH
        ),
        Task(
            title="Implement API endpoints",
            description="Create REST API endpoints for all CRUD operations",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH
        ),
        Task(
            title="Write unit tests",
            description="Create comprehensive unit tests for all components",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM
        ),
        Task(
            title="Deploy to production",
            description="Deploy the application to production environment",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH
        )
    ]
    
    # Create tasks in storage
    created_tasks = []
    for task in tasks:
        created = task_manager.storage.create_task(task)
        created_tasks.append(created)
        print(f"Created task: {created.title} (ID: {created.id})")
    
    print("\n" + "-" * 50 + "\n")
    
    # Demo 1: Task Decomposition
    print("DEMO 1: AI-Powered Task Decomposition")
    print("Decomposing 'Implement API endpoints' task...")
    
    api_task = created_tasks[1]  # The API task
    decompose_result = await decompose_task(
        task_id=api_task.id,
        depth=2,
        max_subtasks=6,
        auto_create=True
    )
    
    if decompose_result.get("success"):
        print("✓ Decomposition successful!")
        print(f"  Model: {decompose_result.get('model', 'unknown')}")
        print(f"  Created {len(decompose_result.get('subtasks', []))} subtasks")
        
        # Show the subtasks
        updated_task = task_manager.storage.get_task(api_task.id)
        if updated_task and updated_task.subtasks:
            print("\n  Subtasks:")
            for i, st in enumerate(updated_task.subtasks, 1):
                print(f"    {i}. {st.title}")
                print(f"       Estimated: {st.estimated_hours}h")
    else:
        print(f"✗ Decomposition failed: {decompose_result.get('error')}")
    
    print("\n" + "-" * 50 + "\n")
    
    # Demo 2: Complexity Analysis
    print("DEMO 2: AI-Powered Complexity Analysis")
    print("Analyzing complexity of 'Implement API endpoints' task...")
    
    complexity_result = await analyze_task_complexity(
        task_id=api_task.id,
        include_subtasks=True
    )
    
    if complexity_result.get("success"):
        print("✓ Complexity analysis successful!")
        analysis = complexity_result.get("analysis", {})
        print(f"  Complexity Score: {analysis.get('complexity_score', 'N/A')}/10")
        print(f"  Complexity Level: {analysis.get('complexity_level', 'N/A')}")
        
        if 'factors' in analysis:
            print("\n  Complexity Factors:")
            for factor, score in analysis['factors'].items():
                print(f"    - {factor.replace('_', ' ').title()}: {score}/10")
    else:
        print(f"✗ Complexity analysis failed: {complexity_result.get('error')}")
    
    print("\n" + "-" * 50 + "\n")
    
    # Demo 3: Task Ordering
    print("DEMO 3: AI-Powered Task Ordering")
    print("Getting optimal execution order for all tasks...")
    
    order_result = await suggest_task_order(
        task_ids=[t.id for t in created_tasks],
        status_filter="pending"
    )
    
    if order_result.get("success"):
        print("✓ Task ordering successful!")
        order_data = order_result.get("order", {})
        
        if 'execution_order' in order_data:
            print("\n  Recommended Execution Order:")
            for item in order_data['execution_order']:
                task = next((t for t in created_tasks if t.id == item['task_id']), None)
                if task:
                    print(f"    {item['order']}. {task.title}")
                    if 'reasoning' in item:
                        print(f"       Reason: {item['reasoning']}")
        
        if 'critical_path' in order_data:
            print(f"\n  Critical Path: {len(order_data['critical_path'])} tasks")
    else:
        print(f"✗ Task ordering failed: {order_result.get('error')}")
    
    print("\n" + "-" * 50 + "\n")
    
    # Demo 4: Generate Subtasks from Description
    print("DEMO 4: Generate Subtasks from Description")
    print("Generating subtasks for a new feature...")
    
    subtasks_result = await generate_subtasks(
        title="Implement real-time notifications",
        description="Add WebSocket-based real-time notifications for user activities, including message notifications, system alerts, and activity updates",
        auto_create_task=True
    )
    
    if subtasks_result.get("success"):
        print("✓ Subtask generation successful!")
        print(f"  Created parent task: {subtasks_result.get('parent_task_id')}")
        print(f"  Generated {len(subtasks_result.get('subtasks', []))} subtasks")
        
        if subtasks_result.get('subtasks'):
            print("\n  Generated Subtasks:")
            for i, st in enumerate(subtasks_result['subtasks'], 1):
                print(f"    {i}. {st.get('title', 'Unknown')}")
    else:
        print(f"✗ Subtask generation failed: {subtasks_result.get('error')}")
    
    # Cleanup
    print("\n" + "-" * 50 + "\n")
    print("Cleaning up test data...")
    
    # Delete all created tasks
    for task in created_tasks:
        task_manager.storage.delete_task(task.id)
    
    # Delete the generated task if it was created
    if subtasks_result.get("parent_task_id"):
        task_manager.storage.delete_task(subtasks_result["parent_task_id"])
    
    print("✓ Cleanup complete")
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    print("Metis CI Features Demo")
    print("=" * 50)
    print()
    print("Note: This demo works best when Rhetor is properly configured")
    print("Currently using fallback adapter which provides limited functionality")
    print()
    
    asyncio.run(demo_ai_features())