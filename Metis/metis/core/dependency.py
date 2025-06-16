"""
Dependency management for Metis

This module provides functionality for managing task dependencies,
including dependency validation, cycle detection, and dependency resolution.
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from metis.models.dependency import Dependency, DependencyManager
from metis.models.task import Task


class DependencyResolver:
    """
    Resolver for task dependencies.
    
    This class provides tools for resolving task dependencies, determining
    task execution order, and detecting dependency issues.
    """
    
    @staticmethod
    def get_execution_order(tasks: List[Task]) -> List[str]:
        """
        Determine a valid execution order for a set of tasks based on dependencies.
        
        Args:
            tasks: List of tasks
            
        Returns:
            List[str]: List of task IDs in valid execution order
            
        Raises:
            ValueError: If there are cyclic dependencies
        """
        # Build dependency graph
        graph: Dict[str, List[str]] = {}
        for task in tasks:
            graph[task.id] = task.dependencies
        
        # Check for cycles
        DependencyResolver._check_cycles(graph)
        
        # Topological sort
        return DependencyResolver._topological_sort(graph)
    
    @staticmethod
    def check_dependency_issues(tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Check for dependency issues in a set of tasks.
        
        Args:
            tasks: List of tasks
            
        Returns:
            List[Dict[str, Any]]: List of issues with their descriptions
        """
        issues = []
        
        # Build task dictionary for quick lookup
        task_dict = {task.id: task for task in tasks}
        
        # Check for missing dependencies
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_dict:
                    issues.append({
                        "type": "missing_dependency",
                        "task_id": task.id,
                        "dependency_id": dep_id,
                        "description": f"Task {task.id} depends on missing task {dep_id}"
                    })
        
        # Try to detect potential circular dependencies
        try:
            DependencyResolver.get_execution_order(tasks)
        except ValueError as e:
            issues.append({
                "type": "circular_dependency",
                "description": str(e)
            })
        
        return issues
    
    @staticmethod
    def get_critical_path(tasks: List[Task]) -> List[str]:
        """
        Determine the critical path through the task dependency graph.
        
        The critical path is the sequence of tasks that must be completed
        to finish the project in the minimum amount of time.
        
        Args:
            tasks: List of tasks
            
        Returns:
            List[str]: List of task IDs in the critical path
            
        Raises:
            ValueError: If there are cyclic dependencies
        """
        # Check for cycles
        graph: Dict[str, List[str]] = {task.id: task.dependencies for task in tasks}
        DependencyResolver._check_cycles(graph)
        
        # Build task dictionary for quick lookup
        task_dict = {task.id: task for task in tasks}
        
        # Calculate earliest finish times
        earliest_finish = {}
        
        # Helper function for recursive calculation
        def calculate_earliest_finish(task_id: str) -> int:
            if task_id in earliest_finish:
                return earliest_finish[task_id]
            
            if task_id not in task_dict:
                return 0
            
            task = task_dict[task_id]
            
            # Default complexity score of 3 if not specified
            complexity = 3
            if task.complexity:
                complexity = int(task.complexity.overall_score)
            
            # Calculate earliest finish time
            if not task.dependencies:
                earliest_finish[task_id] = complexity
                return complexity
            
            max_predecessor = 0
            for dep_id in task.dependencies:
                predecessor_finish = calculate_earliest_finish(dep_id)
                max_predecessor = max(max_predecessor, predecessor_finish)
            
            earliest_finish[task_id] = max_predecessor + complexity
            return earliest_finish[task_id]
        
        # Calculate earliest finish for all tasks
        for task in tasks:
            calculate_earliest_finish(task.id)
        
        # Calculate latest finish times
        latest_finish = {}
        
        # Find the maximum earliest finish time
        max_finish = max(earliest_finish.values()) if earliest_finish else 0
        
        # Find tasks with no dependents
        dependents = {task_id: [] for task_id in task_dict.keys()}
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in dependents:
                    dependents[dep_id].append(task.id)
        
        end_tasks = [
            task_id for task_id in task_dict.keys() 
            if not dependents[task_id]
        ]
        
        # Initialize latest finish times for end tasks
        for task_id in end_tasks:
            latest_finish[task_id] = max_finish
        
        # Helper function for recursive calculation
        def calculate_latest_finish(task_id: str) -> int:
            if task_id in latest_finish:
                return latest_finish[task_id]
            
            if task_id not in task_dict:
                return max_finish
            
            task = task_dict[task_id]
            
            # Default complexity score of 3 if not specified
            complexity = 3
            if task.complexity:
                complexity = int(task.complexity.overall_score)
            
            # Calculate latest finish time
            min_dependent = max_finish
            dependent_tasks = dependents[task_id]
            
            if not dependent_tasks:
                latest_finish[task_id] = max_finish
                return max_finish
            
            for dep_id in dependent_tasks:
                dependent_latest = calculate_latest_finish(dep_id)
                dependent_task = task_dict[dep_id]
                dependent_complexity = 3
                if dependent_task.complexity:
                    dependent_complexity = int(dependent_task.complexity.overall_score)
                min_dependent = min(min_dependent, dependent_latest - dependent_complexity)
            
            latest_finish[task_id] = min_dependent
            return min_dependent
        
        # Calculate latest finish for all tasks
        for task in tasks:
            calculate_latest_finish(task.id)
        
        # Calculate slack
        slack = {}
        for task_id in task_dict.keys():
            slack[task_id] = latest_finish[task_id] - earliest_finish[task_id]
        
        # Tasks with zero slack are on the critical path
        critical_path_tasks = [task_id for task_id, slack_value in slack.items() if slack_value == 0]
        
        # Sort critical path tasks by earliest finish
        critical_path_tasks.sort(key=lambda task_id: earliest_finish[task_id])
        
        return critical_path_tasks
    
    @staticmethod
    def _check_cycles(graph: Dict[str, List[str]]) -> None:
        """
        Check for cycles in the dependency graph.
        
        Args:
            graph: Dependency graph (task_id -> list of dependency IDs)
            
        Raises:
            ValueError: If cycles are detected, with description of the cycle
        """
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            """DFS helper function to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected, find the cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycle_str = " -> ".join(cycle)
                    raise ValueError(f"Cyclic dependency detected: {cycle_str}")
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        # Run DFS on each node to detect cycles
        for node in graph:
            if node not in visited:
                dfs(node)
    
    @staticmethod
    def _topological_sort(graph: Dict[str, List[str]]) -> List[str]:
        """
        Perform a topological sort on the dependency graph.
        
        Args:
            graph: Dependency graph (task_id -> list of dependency IDs)
            
        Returns:
            List[str]: Task IDs in topological order
        """
        result = []
        visited = set()
        
        def dfs(node: str) -> None:
            """DFS helper function for topological sort."""
            visited.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
            
            result.append(node)
        
        # Run DFS on each node to build topological order
        for node in graph:
            if node not in visited:
                dfs(node)
        
        # Result is in reverse topological order, so reverse it
        result.reverse()
        return result