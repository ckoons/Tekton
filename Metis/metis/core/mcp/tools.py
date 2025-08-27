"""
MCP tool definitions for Metis task management.

This module defines FastMCP tools that provide programmatic access
to Metis task management capabilities.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from metis.core.task_manager import TaskManager
from metis.core.task_decomposer import TaskDecomposer
from metis.models.enums import TaskStatus

logger = logging.getLogger("metis.mcp.tools")

# Initialize shared instances
_task_manager = None
_llm_adapter = None
_task_decomposer = None

def get_task_manager() -> TaskManager:
    """Get or create TaskManager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager

def get_llm_adapter() -> MetisLLMAdapter:
    """Get or create LLM adapter instance."""
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = MetisLLMAdapter()
    return _llm_adapter

def get_task_decomposer() -> TaskDecomposer:
    """Get or create TaskDecomposer instance."""
    global _task_decomposer
    if _task_decomposer is None:
        _task_decomposer = TaskDecomposer(get_llm_adapter())
    return _task_decomposer

# Task Management Tools

async def decompose_task(
    task_id: str,
    depth: int = 2,
    max_subtasks: int = 10,
    auto_create: bool = True
) -> Dict[str, Any]:
    """
    Decompose a task into subtasks using AI.
    
    Args:
        task_id: ID of the task to decompose
        depth: Maximum decomposition depth (1-5)
        max_subtasks: Maximum number of subtasks to create (1-20)
        auto_create: Whether to automatically create subtasks
        
    Returns:
        Dictionary containing decomposition results
    """
    try:
        task_manager = get_task_manager()
        task_decomposer = get_task_decomposer()
        
        # Get the task (storage method is sync)
        task = task_manager.storage.get_task(task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found"
            }
        
        # Decompose the task
        result = await task_decomposer.decompose_task(
            task=task,
            depth=depth,
            max_subtasks=max_subtasks,
            auto_create=auto_create
        )
        
        # If auto_create is True and successful, add subtasks to task manager
        if result.get("success") and auto_create and result.get("subtasks"):
            for subtask in result["subtasks"]:
                task.add_subtask(subtask)
            
            # Update task in storage
            task_manager.storage.update_task(task_id, {"subtasks": task.subtasks})
        
        return result
        
    except Exception as e:
        logger.error(f"Error in decompose_task: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def analyze_task_complexity(
    task_id: str,
    include_subtasks: bool = True
) -> Dict[str, Any]:
    """
    Analyze task complexity using AI.
    
    Args:
        task_id: ID of the task to analyze
        include_subtasks: Whether to include subtasks in analysis
        
    Returns:
        Dictionary containing complexity analysis
    """
    try:
        task_manager = get_task_manager()
        llm_adapter = get_llm_adapter()
        
        # Get the task (storage method is sync)
        task = task_manager.storage.get_task(task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found"
            }
        
        # Get subtasks if requested
        subtasks = None
        if include_subtasks:
            subtasks = [
                {
                    "title": st.title,
                    "description": st.description,
                    "estimated_hours": st.estimated_hours,
                    "complexity": st.complexity.overall_score if st.complexity else 5
                }
                for st in task.subtasks
            ]
        
        # Analyze complexity
        result = await llm_adapter.analyze_task_complexity(
            task_title=task.title,
            task_description=task.description or "",
            subtasks=subtasks
        )
        
        # If successful, update task complexity
        if result.get("success") and result.get("analysis"):
            analysis = result["analysis"]
            if "complexity_score" in analysis:
                # Update task complexity directly on the task
                if hasattr(task, 'complexity') and task.complexity:
                    task.complexity.overall_score = analysis["complexity_score"]
                    task_manager.storage.update_task(task_id, {"complexity": task.complexity})
        
        return result
        
    except Exception as e:
        logger.error(f"Error in analyze_task_complexity: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def suggest_task_order(
    task_ids: Optional[List[str]] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Suggest optimal task execution order.
    
    Args:
        task_ids: List of specific task IDs to order (None for all)
        status_filter: Filter tasks by status (e.g., "pending")
        
    Returns:
        Dictionary containing execution order suggestions
    """
    try:
        task_manager = get_task_manager()
        llm_adapter = get_llm_adapter()
        
        # Get tasks
        if task_ids:
            tasks = [task_manager.storage.get_task(tid) for tid in task_ids]
            tasks = [t for t in tasks if t is not None]
        else:
            tasks = list(task_manager.storage._tasks.values())
            if status_filter:
                status_enum = TaskStatus(status_filter.upper())
                tasks = [t for t in tasks if t.status == status_enum]
        
        if not tasks:
            return {
                "success": False,
                "error": "No tasks found"
            }
        
        # Prepare task data
        task_data = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description or "",
                "estimated_hours": sum(st.estimated_hours for st in t.subtasks) if t.subtasks else 1,
                "priority": t.priority.value if hasattr(t.priority, 'value') else str(t.priority),
                "status": t.status.value if hasattr(t.status, 'value') else str(t.status)
            }
            for t in tasks
        ]
        
        # Get dependencies
        all_deps = []
        for task in tasks:
            # Get dependencies from storage
            deps = [d for d in task_manager.storage._dependencies.values() 
                   if d.from_task_id == task.id or d.to_task_id == task.id]
            for dep in deps:
                all_deps.append({
                    "from_task": dep.from_task_id,
                    "to_task": dep.to_task_id,
                    "type": dep.dependency_type.value if hasattr(dep.dependency_type, 'value') else str(dep.dependency_type)
                })
        
        # Get ordering suggestions
        result = await llm_adapter.suggest_task_order(
            tasks=task_data,
            dependencies=all_deps
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in suggest_task_order: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def generate_subtasks(
    title: str,
    description: str,
    parent_task_id: Optional[str] = None,
    auto_create_task: bool = False
) -> Dict[str, Any]:
    """
    Generate subtasks from a description without requiring an existing task.
    
    Args:
        title: Title for the task
        description: Description to generate subtasks from
        parent_task_id: Optional parent task to attach subtasks to
        auto_create_task: Whether to create a new task if parent_task_id is None
        
    Returns:
        Dictionary containing generated subtasks
    """
    try:
        task_manager = get_task_manager()
        llm_adapter = get_llm_adapter()
        
        # If parent task ID provided, verify it exists
        if parent_task_id:
            parent_task = task_manager.storage.get_task(parent_task_id)
            if not parent_task:
                return {
                    "success": False,
                    "error": f"Parent task {parent_task_id} not found"
                }
        elif auto_create_task:
            # Create a new task
            from metis.models.task import Task
            from metis.models.enums import Priority
            new_task = Task(
                title=title,
                description=description,
                status=TaskStatus.PENDING,
                priority=Priority.MEDIUM
            )
            task_manager.storage.create_task(new_task)
            parent_task_id = new_task.id
        
        # Generate subtasks using LLM
        result = await llm_adapter.decompose_task(
            task_title=title,
            task_description=description,
            depth=2,
            max_subtasks=10
        )
        
        # If successful and we have a parent task, create the subtasks
        if result.get("success") and parent_task_id and result.get("subtasks"):
            task_decomposer = get_task_decomposer()
            created_subtasks = []
            
            for idx, subtask_data in enumerate(result["subtasks"]):
                subtask = task_decomposer._create_subtask_from_data(
                    task_id=parent_task_id,
                    subtask_data=subtask_data,
                    order=idx + 1
                )
                parent_task = task_manager.storage.get_task(parent_task_id)
                if parent_task:
                    parent_task.add_subtask(subtask)
                    task_manager.storage.update_task(parent_task_id, {"subtasks": parent_task.subtasks})
                created_subtasks.append(subtask)
            
            result["created_subtasks"] = created_subtasks
            result["parent_task_id"] = parent_task_id
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_subtasks: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def detect_dependencies(
    task_ids: Optional[List[str]] = None,
    auto_create: bool = False
) -> Dict[str, Any]:
    """
    Detect potential dependencies between tasks using AI.
    
    Args:
        task_ids: List of task IDs to analyze (None for all)
        auto_create: Whether to automatically create detected dependencies
        
    Returns:
        Dictionary containing detected dependencies
    """
    try:
        task_manager = get_task_manager()
        
        # Get tasks
        if task_ids:
            tasks = [task_manager.storage.get_task(tid) for tid in task_ids]
            tasks = [t for t in tasks if t is not None]
        else:
            tasks = list(task_manager.storage._tasks.values())
        
        if len(tasks) < 2:
            return {
                "success": True,
                "dependencies": [],
                "message": "Need at least 2 tasks to detect dependencies"
            }
        
        # For now, return a simple heuristic-based detection
        # In a full implementation, this would use the LLM
        detected = []
        
        for i, task1 in enumerate(tasks):
            for task2 in tasks[i+1:]:
                # Simple heuristic: if one task mentions another's key terms
                task1_words = set(task1.title.lower().split())
                task2_words = set(task2.title.lower().split())
                
                # Check for common technical terms that might indicate dependency
                tech_terms = {"database", "api", "auth", "model", "schema", "test", "deploy"}
                common_tech = (task1_words & tech_terms) & (task2_words & tech_terms)
                
                if common_tech:
                    # Guess dependency direction based on common patterns
                    if any(word in task1.title.lower() for word in ["design", "plan", "schema"]):
                        detected.append({
                            "from_task_id": task1.id,
                            "to_task_id": task2.id,
                            "reason": f"Both tasks involve {', '.join(common_tech)}",
                            "confidence": 0.7
                        })
                    elif any(word in task2.title.lower() for word in ["test", "deploy"]):
                        detected.append({
                            "from_task_id": task1.id,
                            "to_task_id": task2.id,
                            "reason": f"Testing/deployment typically follows implementation",
                            "confidence": 0.8
                        })
        
        # If auto_create, create the dependencies
        if auto_create and detected:
            created = []
            for dep in detected:
                if dep["confidence"] >= 0.7:
                    try:
                        # Create dependency directly in storage
                        from metis.models.dependency import Dependency, DependencyType
                        new_dep = Dependency(
                            from_task_id=dep["from_task_id"],
                            to_task_id=dep["to_task_id"],
                            dependency_type=DependencyType.BLOCKS
                        )
                        task_manager.storage._dependencies[new_dep.id] = new_dep
                        created.append(dep)
                    except Exception as e:
                        logger.warning(f"Could not create dependency: {e}")
            
            return {
                "success": True,
                "dependencies": detected,
                "created": created
            }
        
        return {
            "success": True,
            "dependencies": detected,
            "auto_created": False
        }
        
    except Exception as e:
        logger.error(f"Error in detect_dependencies: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Tool lists for MCP registration
task_management_tools = [
    {
        "name": "decompose_task",
        "description": "Decompose a task into subtasks using AI",
        "function": decompose_task,
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of the task to decompose"
                },
                "depth": {
                    "type": "integer",
                    "description": "Maximum decomposition depth (1-5)",
                    "default": 2
                },
                "max_subtasks": {
                    "type": "integer",
                    "description": "Maximum number of subtasks (1-20)",
                    "default": 10
                },
                "auto_create": {
                    "type": "boolean",
                    "description": "Whether to automatically create subtasks",
                    "default": True
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "analyze_task_complexity",
        "description": "Analyze task complexity using AI",
        "function": analyze_task_complexity,
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of the task to analyze"
                },
                "include_subtasks": {
                    "type": "boolean",
                    "description": "Whether to include subtasks in analysis",
                    "default": True
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "suggest_task_order",
        "description": "Suggest optimal task execution order",
        "function": suggest_task_order,
        "parameters": {
            "type": "object",
            "properties": {
                "task_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of task IDs to order (None for all)"
                },
                "status_filter": {
                    "type": "string",
                    "description": "Filter tasks by status",
                    "enum": ["pending", "in_progress", "completed", "blocked"]
                }
            }
        }
    },
    {
        "name": "generate_subtasks",
        "description": "Generate subtasks from a description",
        "function": generate_subtasks,
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title for the task"
                },
                "description": {
                    "type": "string",
                    "description": "Description to generate subtasks from"
                },
                "parent_task_id": {
                    "type": "string",
                    "description": "Optional parent task ID"
                },
                "auto_create_task": {
                    "type": "boolean",
                    "description": "Create new task if no parent",
                    "default": False
                }
            },
            "required": ["title", "description"]
        }
    },
    {
        "name": "detect_dependencies",
        "description": "Detect potential dependencies between tasks",
        "function": detect_dependencies,
        "parameters": {
            "type": "object",
            "properties": {
                "task_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of task IDs to analyze"
                },
                "auto_create": {
                    "type": "boolean",
                    "description": "Auto-create detected dependencies",
                    "default": False
                }
            }
        }
    }
]

# Dependency Management Tools  
dependency_management_tools = []

# Analytics Tools
analytics_tools = []

# Telos Integration Tools
telos_integration_tools = []

# MCP-enabled task manager class
class MetisTaskManager:
    """MCP-enabled task manager with CI capabilities."""
    
    def __init__(self):
        self.task_manager = get_task_manager()
        self.llm_adapter = get_llm_adapter()
        self.task_decomposer = get_task_decomposer()
    
    async def decompose_task(self, task_id: str, **kwargs):
        """Decompose a task using AI."""
        return await decompose_task(task_id, **kwargs)
    
    async def analyze_complexity(self, task_id: str, **kwargs):
        """Analyze task complexity."""
        return await analyze_task_complexity(task_id, **kwargs)
    
    async def suggest_order(self, **kwargs):
        """Suggest task execution order."""
        return await suggest_task_order(**kwargs)
    
    async def generate_subtasks(self, title: str, description: str, **kwargs):
        """Generate subtasks from description."""
        return await generate_subtasks(title, description, **kwargs)
    
    async def detect_dependencies(self, **kwargs):
        """Detect task dependencies."""
        return await detect_dependencies(**kwargs)