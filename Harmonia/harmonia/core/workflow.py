"""
Workflow - Core workflow representation.

This module defines the data structures for representing workflows and tasks.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum

# Configure logger
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Status of a task execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELED = "canceled"


@dataclass
class Task:
    """
    Represents a single task within a workflow.
    
    Attributes:
        name: Task name (unique within a workflow)
        component: Component responsible for executing the task
        action: Action to be performed by the component
        input: Input data for the task (can include expressions)
        output: Output data schema expected from the task
        depends_on: List of tasks that must complete before this task
        timeout: Timeout in seconds (optional)
        retry: Number of retries on failure (optional)
        id: Unique identifier for the task
        metadata: Additional task metadata
    """
    
    name: str
    component: str
    action: str
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retry: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary representation.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "name": self.name,
            "component": self.component,
            "action": self.action,
            "input": self.input,
            "output": self.output,
            "depends_on": self.depends_on,
            "timeout": self.timeout,
            "retry": self.retry,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task from dictionary representation.
        
        Args:
            data: Dictionary representation of the task
            
        Returns:
            Task instance
        """
        return cls(
            name=data["name"],
            component=data["component"],
            action=data["action"],
            input=data.get("input", {}),
            output=data.get("output", {}),
            depends_on=data.get("depends_on", []),
            timeout=data.get("timeout"),
            retry=data.get("retry"),
            id=data.get("id", str(uuid.uuid4())),
            metadata=data.get("metadata", {})
        )


@dataclass
class Workflow:
    """
    Represents a complete workflow definition.
    
    Attributes:
        name: Workflow name
        description: Workflow description
        tasks: Dictionary of tasks by name
        input: Input schema for the workflow
        output: Output schema for the workflow
        id: Unique identifier for the workflow
        version: Workflow version
        metadata: Additional workflow metadata
    """
    
    name: str
    description: str = ""
    tasks: Dict[str, Task] = field(default_factory=dict)
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the workflow.
        
        Args:
            task: Task to add
        """
        if task.name in self.tasks:
            logger.warning(f"Task {task.name} already exists in workflow {self.name}, overwriting")
        
        self.tasks[task.name] = task
        logger.info(f"Added task {task.name} to workflow {self.name}")
    
    def get_task(self, task_name: str) -> Optional[Task]:
        """
        Get a task by name.
        
        Args:
            task_name: Name of the task to get
            
        Returns:
            Task instance or None if not found
        """
        return self.tasks.get(task_name)
    
    def remove_task(self, task_name: str) -> bool:
        """
        Remove a task by name.
        
        Args:
            task_name: Name of the task to remove
            
        Returns:
            True if the task was removed
        """
        if task_name in self.tasks:
            del self.tasks[task_name]
            logger.info(f"Removed task {task_name} from workflow {self.name}")
            return True
        
        logger.warning(f"Task {task_name} not found in workflow {self.name}")
        return False
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Generate a dependency graph for the workflow.
        
        Returns:
            Dictionary mapping task names to sets of dependent task names
        """
        graph = {}
        
        for task_name, task in self.tasks.items():
            graph[task_name] = set()
            
            for dep_name in task.depends_on:
                if dep_name in self.tasks:
                    graph[task_name].add(dep_name)
        
        return graph
    
    def get_root_tasks(self) -> List[Task]:
        """
        Get tasks with no dependencies (roots of the workflow).
        
        Returns:
            List of root tasks
        """
        return [task for task in self.tasks.values() if not task.depends_on]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert workflow to dictionary representation.
        
        Returns:
            Dictionary representation of the workflow
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": {name: task.to_dict() for name, task in self.tasks.items()},
            "input": self.input,
            "output": self.output,
            "version": self.version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """
        Create a workflow from dictionary representation.
        
        Args:
            data: Dictionary representation of the workflow
            
        Returns:
            Workflow instance
        """
        workflow = cls(
            name=data["name"],
            description=data.get("description", ""),
            input=data.get("input", {}),
            output=data.get("output", {}),
            id=data.get("id", str(uuid.uuid4())),
            version=data.get("version", "1.0"),
            metadata=data.get("metadata", {})
        )
        
        # Add tasks
        tasks_data = data.get("tasks", {})
        for task_name, task_data in tasks_data.items():
            task = Task.from_dict(task_data)
            workflow.add_task(task)
        
        return workflow