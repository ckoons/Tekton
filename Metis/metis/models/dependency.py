"""
Dependency models for Metis

This module defines the models for task dependencies in the Metis system.
Dependencies represent relationships between tasks that constrain their execution.
"""

from datetime import datetime
from pydantic import Field
from uuid import uuid4
from typing import Optional, List, Dict, Any, Set
from tekton.models.base import TektonBaseModel


class DependencyType(str):
    """String enum-like constants for dependency types."""
    BLOCKS = "blocks"  # Task is blocked by another task
    DEPENDS_ON = "depends_on"  # Task depends on another task
    RELATED_TO = "related_to"  # Tasks are related but not blocking


class Dependency(TektonBaseModel):
    """
    Model representing a dependency between two tasks.
    
    Dependencies define relationships between tasks and may constrain
    when tasks can be started or completed.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_task_id: str  # ID of the source task
    target_task_id: str  # ID of the target task
    dependency_type: str = DependencyType.DEPENDS_ON
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update dependency fields.
        
        Args:
            updates: Dictionary of field updates
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamp
        self.updated_at = datetime.utcnow()


class DependencyManager:
    """
    Manager for handling task dependencies.
    
    Provides functionality for managing dependencies between tasks,
    including detection of circular dependencies.
    """
    
    @staticmethod
    def validate_new_dependency(
        dependencies: List[Dependency], 
        source_id: str, 
        target_id: str
    ) -> bool:
        """
        Validate that a new dependency would not create a circular reference.
        
        Args:
            dependencies: Existing dependencies
            source_id: Source task ID for the new dependency
            target_id: Target task ID for the new dependency
            
        Returns:
            bool: True if the dependency is valid, False if it would create a cycle
        """
        # If source and target are the same, it's invalid
        if source_id == target_id:
            return False
            
        # Build a graph of dependencies
        graph: Dict[str, Set[str]] = {}
        
        # Add all existing dependencies to the graph
        for dep in dependencies:
            if dep.source_task_id not in graph:
                graph[dep.source_task_id] = set()
            graph[dep.source_task_id].add(dep.target_task_id)
        
        # Add the new dependency to check
        if source_id not in graph:
            graph[source_id] = set()
        graph[source_id].add(target_id)
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def is_cyclic_util(node: str) -> bool:
            """Helper function for cycle detection."""
            visited.add(node)
            rec_stack.add(node)
            
            # Visit all neighbors
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    if is_cyclic_util(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check for cycles starting from each node
        for node in graph:
            if node not in visited:
                if is_cyclic_util(node):
                    return False  # Cycle detected, dependency is invalid
        
        return True  # No cycles found, dependency is valid
    
    @staticmethod
    def get_blocking_tasks(dependencies: List[Dependency], task_id: str) -> List[str]:
        """
        Get the IDs of tasks that block a given task.
        
        Args:
            dependencies: List of all dependencies
            task_id: ID of the task to check
            
        Returns:
            List[str]: List of task IDs that block the specified task
        """
        blocking_tasks = []
        
        for dep in dependencies:
            if (dep.target_task_id == task_id and 
                dep.dependency_type in (DependencyType.BLOCKS, DependencyType.DEPENDS_ON)):
                blocking_tasks.append(dep.source_task_id)
        
        return blocking_tasks
    
    @staticmethod
    def get_dependent_tasks(dependencies: List[Dependency], task_id: str) -> List[str]:
        """
        Get the IDs of tasks that depend on a given task.
        
        Args:
            dependencies: List of all dependencies
            task_id: ID of the task to check
            
        Returns:
            List[str]: List of task IDs that depend on the specified task
        """
        dependent_tasks = []
        
        for dep in dependencies:
            if (dep.source_task_id == task_id and 
                dep.dependency_type in (DependencyType.BLOCKS, DependencyType.DEPENDS_ON)):
                dependent_tasks.append(dep.target_task_id)
        
        return dependent_tasks