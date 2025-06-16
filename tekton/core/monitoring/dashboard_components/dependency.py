#!/usr/bin/env python3
"""
Dependency Management Component

This module provides dependency tracking and visualization for the dashboard.
"""

import time
from typing import Dict, List, Any, Optional, Callable

from ...logging_integration import get_logger, LogCategory

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.dependency")


class DependencyManager:
    """
    Dependency graph management for components.
    
    Tracks component dependencies, detects cycles, and visualizes the 
    dependency graph.
    """
    
    def __init__(self, dashboard=None):
        """
        Initialize dependency manager.
        
        Args:
            dashboard: Dashboard instance
        """
        self.dashboard = dashboard
        self.dependency_graph = {}
        
    def update_dependency_graph(self):
        """Update the dependency graph from components."""
        if not self.dashboard or not hasattr(self.dashboard, "component_status"):
            return
            
        # Build dependency graph
        self.dependency_graph = build_dependency_graph(self.dashboard.component_status)
        
        # Check for dependency cycles
        cycles = detect_dependency_cycles(self.dependency_graph)
        if cycles:
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                logger.warning(f"Dependency cycle detected: {cycle_str}")
                
                # Generate alert if dashboard has alert capability
                if hasattr(self.dashboard, "_generate_alert"):
                    from ..alerts import AlertSeverity
                    self.dashboard._generate_alert(
                        severity=AlertSeverity.WARNING,
                        title="Dependency Cycle Detected",
                        description=f"Circular dependency detected between components: {cycle_str}",
                        component_id=None
                    )
        
        # Update dashboard dependency graph
        if hasattr(self.dashboard, "dependency_graph"):
            self.dashboard.dependency_graph = self.dependency_graph
    
    def get_dependency_graph(self):
        """Get the current dependency graph.
        
        Returns:
            Dependency graph dictionary
        """
        return self.dependency_graph
    
    def get_component_dependencies(self, component_id: str):
        """Get dependencies for a specific component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            List of component IDs that this component depends on
        """
        return self.dependency_graph.get(component_id, {}).get("dependencies", [])
    
    def get_component_dependents(self, component_id: str):
        """Get components that depend on this component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            List of component IDs that depend on this component
        """
        return self.dependency_graph.get(component_id, {}).get("dependents", [])


def build_dependency_graph(components: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, List[str]]]:
    """Build a dependency graph from component data.
    
    Args:
        components: Dictionary of component data
        
    Returns:
        Dependency graph dictionary
    """
    # Initialize graph
    graph = {}
    
    # First pass: initialize all components in graph
    for component_id in components.keys():
        graph[component_id] = {
            "dependencies": [],
            "dependents": []
        }
    
    # Second pass: add dependencies and dependents
    for component_id, component in components.items():
        # Extract dependencies
        dependencies = component.get("dependencies", [])
        
        # Update graph
        if component_id in graph:
            graph[component_id]["dependencies"] = dependencies
            
            # Add this component as a dependent to each dependency
            for dep_id in dependencies:
                if dep_id in graph:
                    if component_id not in graph[dep_id]["dependents"]:
                        graph[dep_id]["dependents"].append(component_id)
    
    return graph


def detect_dependency_cycles(graph: Dict[str, Dict[str, List[str]]]) -> List[List[str]]:
    """Detect cycles in dependency graph.
    
    Args:
        graph: Dependency graph dictionary
        
    Returns:
        List of dependency cycles (each cycle is a list of component IDs)
    """
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node, path):
        nonlocal cycles, visited, rec_stack
        
        # Mark current node as visited and add to recursion stack
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        # Visit all dependencies
        for dependency in graph.get(node, {}).get("dependencies", []):
            # If not visited, recurse
            if dependency not in visited:
                dfs(dependency, path.copy())
            # If in recursion stack, we found a cycle
            elif dependency in rec_stack:
                # Find start of cycle
                start_index = path.index(dependency)
                cycle = path[start_index:] + [dependency]
                cycles.append(cycle)
        
        # Remove from recursion stack
        rec_stack.remove(node)
    
    # Check all nodes
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    return cycles
