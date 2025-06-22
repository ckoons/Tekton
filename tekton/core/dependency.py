#!/usr/bin/env python3
"""
Dependency Resolution Module

This module provides utilities for resolving component dependencies,
detecting and breaking dependency cycles to prevent startup deadlocks.
"""

import logging
from typing import Dict, List, Tuple, Set
from landmarks import architecture_decision, danger_zone, performance_boundary

logger = logging.getLogger("tekton.dependency")

@architecture_decision(
    title="Cycle-breaking dependency resolver",
    rationale="Automatically detect and break circular dependencies to prevent startup deadlocks",
    alternatives_considered=["Manual dependency ordering", "Fail on cycles", "Lazy loading"])
class DependencyResolver:
    """
    Utility for resolving component dependencies with cycle detection.
    
    Detects and handles circular dependencies to prevent deadlocks during startup.
    """
    
    @danger_zone(
        title="Dependency cycle detection",
        risk_level="startup_failure",
        mitigation="Automatically break cycles by removing lowest priority edges",
        review_required="Verify cycle breaking doesn't violate critical dependencies"
    )
    @staticmethod
    def detect_cycles(dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Detect cycles in a dependency graph.
        
        Args:
            dependency_graph: Graph of dependencies (component_id -> list of dependency_ids)
            
        Returns:
            List of detected cycles
        """
        visited = set()
        path = []
        cycles = []
        
        def dfs(node):
            if node in path:
                # Cycle detected
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
                
            if node in visited:
                return
                
            visited.add(node)
            path.append(node)
            
            for dep in dependency_graph.get(node, []):
                dfs(dep)
                
            path.pop()
            
        for node in dependency_graph:
            dfs(node)
            
        return cycles
    
    @performance_boundary(
        title="Dependency resolution",
        sla="<100ms for typical graph",
        metrics={"components": "100", "edges": "500", "time": "50ms"},
        optimization_notes="DFS cycle detection, topological sort with priority queue"
    )
    @staticmethod
    def resolve_dependencies(dependency_graph: Dict[str, List[str]]) -> Tuple[List[str], bool]:
        """
        Resolve dependencies in topological order with cycle detection.
        
        Args:
            dependency_graph: Graph of dependencies (component_id -> list of dependency_ids)
            
        Returns:
            Tuple of (ordered_components, had_cycles)
        """
        # Detect and break cycles
        had_cycles = False
        cycles = DependencyResolver.detect_cycles(dependency_graph)
        if cycles:
            had_cycles = True
            logger.warning(f"Detected dependency cycles: {cycles}")
            
            # Break each cycle by removing the last dependency
            for cycle in cycles:
                from_node = cycle[-2]
                to_node = cycle[-1]
                
                if from_node in dependency_graph and to_node in dependency_graph.get(from_node, []):
                    logger.warning(f"Breaking dependency cycle by removing {from_node} -> {to_node}")
                    dependency_graph[from_node].remove(to_node)
        
        # Perform topological sort on the (now acyclic) graph
        in_degree = {node: 0 for node in dependency_graph}
        for node, deps in dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Start with nodes that have no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Process node with no dependencies
            node = queue.pop(0)
            result.append(node)
            
            # Reduce in-degree of all nodes that depend on this one
            for dependent in [n for n, deps in dependency_graph.items() if node in deps]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check if all nodes were included
        if len(result) != len(dependency_graph):
            logger.error("Unable to resolve all dependencies - graph may still have cycles")
            # Add missing nodes in some order
            for node in dependency_graph:
                if node not in result:
                    result.append(node)
        
        return result, had_cycles
    
    def __init__(self):
        """Initialize the dependency resolver."""
        self.dependency_graph = {}
        self.component_priorities = {}
    
    async def add_component(self, component_id: str, dependencies: List[str], priority: int = 0) -> None:
        """
        Add a component and its dependencies to the graph.
        
        Args:
            component_id: The component ID
            dependencies: List of component dependencies
            priority: Component priority (higher values indicate higher priority)
        """
        self.dependency_graph[component_id] = dependencies
        self.component_priorities[component_id] = priority
        logger.debug(f"Added component {component_id} with dependencies {dependencies}")
        
    async def remove_component(self, component_id: str) -> None:
        """
        Remove a component from the dependency graph.
        
        Args:
            component_id: The component ID to remove
        """
        if component_id in self.dependency_graph:
            del self.dependency_graph[component_id]
            
        if component_id in self.component_priorities:
            del self.component_priorities[component_id]
            
        # Remove component from other dependencies
        for deps in self.dependency_graph.values():
            if component_id in deps:
                deps.remove(component_id)
                
        logger.debug(f"Removed component {component_id} from dependency graph")
        
    async def resolve_cycles(self) -> List[List[str]]:
        """
        Detect and resolve dependency cycles by breaking the lowest priority edge.
        
        Returns:
            List of cycles that were resolved
        """
        cycles = self.detect_cycles(self.dependency_graph)
        if not cycles:
            return []
            
        resolved_cycles = []
        
        for cycle in cycles:
            # Find the lowest priority edge to break
            lowest_priority = float('inf')
            edge_to_break = (None, None)
            
            for i in range(len(cycle) - 1):
                from_node = cycle[i]
                to_node = cycle[i + 1]
                
                # Calculate edge priority based on node priorities
                from_priority = self.component_priorities.get(from_node, 0)
                to_priority = self.component_priorities.get(to_node, 0)
                edge_priority = from_priority + to_priority
                
                if edge_priority < lowest_priority:
                    lowest_priority = edge_priority
                    edge_to_break = (from_node, to_node)
                    
            # Break the edge
            from_node, to_node = edge_to_break
            if from_node and to_node and to_node in self.dependency_graph.get(from_node, []):
                logger.warning(f"Breaking dependency cycle by removing {from_node} -> {to_node}")
                self.dependency_graph[from_node].remove(to_node)
                resolved_cycles.append(cycle)
        
        return resolved_cycles
        
    async def get_startup_order(self) -> List[str]:
        """
        Get the optimal startup order for components based on dependencies.
        
        Returns:
            List of component IDs in startup order
        """
        ordered, _ = self.resolve_dependencies(self.dependency_graph)
        return ordered
        
    async def check_dependencies_satisfied(self, 
                                     component_id: str, 
                                     dependencies: List[str],
                                     running_components: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if all dependencies for a component are satisfied.
        
        Args:
            component_id: Component ID
            dependencies: List of dependencies to check
            running_components: List of components that are currently running
            
        Returns:
            Tuple of (all_satisfied, missing_dependencies)
        """
        if not dependencies:
            return True, []
            
        missing = [dep for dep in dependencies if dep not in running_components]
        
        return len(missing) == 0, missing