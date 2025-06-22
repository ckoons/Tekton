"""
Critical Path Analysis Module

This module implements critical path analysis for project plans, identifying
the sequence of tasks that determine the minimum project duration.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx
from datetime import datetime, timedelta

from ..models.plan import Plan
from ..models.task import Task
from landmarks import architecture_decision, performance_boundary, danger_zone

logger = logging.getLogger("prometheus.critical_path")

@architecture_decision(
    title="Graph-based critical path analysis",
    rationale="Use NetworkX directed graphs for efficient critical path calculation with support for complex dependency chains",
    alternatives=["PERT charts", "Gantt chart analysis", "Manual dependency tracking"],
    decision_date="2024-02-20"
)
@danger_zone(
    title="Critical path calculation",
    risk_level="high",
    risks=["Circular dependencies", "Incorrect duration estimates", "Missing dependencies"],
    mitigations=["Cycle detection", "Validation checks", "Conservative estimates"],
    review_required=True
)
class CriticalPathAnalyzer:
    """
    Analyzer for calculating critical path and related metrics.
    
    The critical path is the sequence of tasks that determines the minimum 
    duration of the project. If any task on the critical path is delayed, 
    the entire project will be delayed.
    """
    
    def __init__(self):
        """Initialize the critical path analyzer."""
        self.graph = None
        self.critical_path = []
        self.earliest_start_times = {}
        self.earliest_finish_times = {}
        self.latest_start_times = {}
        self.latest_finish_times = {}
        self.slack_times = {}
    
    async def analyze_plan(self, plan: Plan) -> Dict:
        """
        Analyze a plan to determine the critical path and related metrics.
        
        Args:
            plan: The project plan to analyze
            
        Returns:
            Dictionary containing critical path and related metrics
        """
        logger.info(f"Analyzing critical path for plan: {plan.name}")
        
        # Build a directed graph from the plan tasks
        self.graph = self._build_task_graph(plan)
        
        # Calculate earliest and latest times
        self._calculate_earliest_times()
        self._calculate_latest_times()
        
        # Calculate slack for each task
        self._calculate_slack()
        
        # Identify the critical path
        self.critical_path = self._identify_critical_path()
        
        # Build the result dictionary
        result = {
            "critical_path": [task_id for task_id in self.critical_path],
            "critical_path_tasks": [plan.get_task(task_id) for task_id in self.critical_path],
            "critical_path_duration": self._calculate_path_duration(self.critical_path),
            "earliest_start": self.earliest_start_times,
            "earliest_finish": self.earliest_finish_times,
            "latest_start": self.latest_start_times,
            "latest_finish": self.latest_finish_times,
            "slack": self.slack_times,
            "total_tasks": len(plan.tasks),
            "critical_tasks": len(self.critical_path),
            "critical_ratio": len(self.critical_path) / len(plan.tasks) if plan.tasks else 0,
            "bottlenecks": self._identify_bottlenecks()
        }
        
        logger.info(f"Critical path analysis complete. Duration: {result['critical_path_duration']}")
        
        return result
    
    def _build_task_graph(self, plan: Plan) -> nx.DiGraph:
        """
        Build a directed graph from the plan's tasks and dependencies.
        
        Args:
            plan: The project plan
            
        Returns:
            A NetworkX directed graph representing the tasks and dependencies
        """
        graph = nx.DiGraph()
        
        # Add 'start' and 'end' nodes
        graph.add_node("start", duration=0)
        graph.add_node("end", duration=0)
        
        # Add task nodes with their duration
        for task_id, task in plan.tasks.items():
            # Convert duration to number of days/hours for calculation
            duration = self._get_task_duration_hours(task)
            graph.add_node(task_id, duration=duration, task=task)
        
        # Add dependency edges
        for task_id, task in plan.tasks.items():
            if not task.dependencies:
                # Tasks with no dependencies are connected to the start node
                graph.add_edge("start", task_id)
            else:
                # Add edges for each dependency
                for dep_id in task.dependencies:
                    if dep_id in plan.tasks:
                        graph.add_edge(dep_id, task_id)
        
        # Find tasks that aren't prerequisites for any other tasks
        terminal_tasks = []
        for task_id in graph.nodes():
            if task_id != "start" and task_id != "end":
                if len(list(graph.successors(task_id))) == 0:
                    terminal_tasks.append(task_id)
        
        # Connect terminal tasks to the end node
        for task_id in terminal_tasks:
            graph.add_edge(task_id, "end")
        
        return graph
    
    def _calculate_earliest_times(self) -> None:
        """
        Calculate the earliest start and finish times for each task.
        
        Uses a forward pass through the network.
        """
        # Initialize times
        self.earliest_start_times = {node: 0 for node in self.graph.nodes()}
        self.earliest_finish_times = {node: 0 for node in self.graph.nodes()}
        
        # Get a topological sort of the nodes
        for node in nx.topological_sort(self.graph):
            # For the start node, earliest start and finish are 0
            if node == "start":
                self.earliest_start_times[node] = 0
                self.earliest_finish_times[node] = 0
                continue
            
            # Get all predecessors
            predecessors = list(self.graph.predecessors(node))
            
            if predecessors:
                # Earliest start is the maximum of all predecessors' earliest finish times
                self.earliest_start_times[node] = max(
                    self.earliest_finish_times[pred] for pred in predecessors
                )
            else:
                # If no predecessors, earliest start is 0
                self.earliest_start_times[node] = 0
            
            # Earliest finish is earliest start plus duration
            duration = self.graph.nodes[node].get("duration", 0)
            self.earliest_finish_times[node] = self.earliest_start_times[node] + duration
    
    def _calculate_latest_times(self) -> None:
        """
        Calculate the latest start and finish times for each task.
        
        Uses a backward pass through the network.
        """
        # Initialize times
        self.latest_start_times = {node: float('inf') for node in self.graph.nodes()}
        self.latest_finish_times = {node: float('inf') for node in self.graph.nodes()}
        
        # The latest finish of the end node is the earliest finish
        end_node = "end"
        self.latest_finish_times[end_node] = self.earliest_finish_times[end_node]
        self.latest_start_times[end_node] = self.latest_finish_times[end_node]
        
        # Get a reverse topological sort of the nodes
        for node in reversed(list(nx.topological_sort(self.graph))):
            # For the end node, we've already set the values
            if node == end_node:
                continue
            
            # Get all successors
            successors = list(self.graph.successors(node))
            
            if successors:
                # Latest finish is the minimum of all successors' latest start times
                self.latest_finish_times[node] = min(
                    self.latest_start_times[succ] for succ in successors
                )
            else:
                # If no successors, latest finish is the same as the earliest finish
                self.latest_finish_times[node] = self.earliest_finish_times[end_node]
            
            # Latest start is latest finish minus duration
            duration = self.graph.nodes[node].get("duration", 0)
            self.latest_start_times[node] = self.latest_finish_times[node] - duration
    
    def _calculate_slack(self) -> None:
        """
        Calculate the slack time for each task.
        
        Slack is the amount of time a task can be delayed without delaying the project.
        """
        self.slack_times = {}
        
        for node in self.graph.nodes():
            if node not in ("start", "end"):
                # Slack is the difference between latest and earliest start times
                self.slack_times[node] = self.latest_start_times[node] - self.earliest_start_times[node]
    
    def _identify_critical_path(self) -> List[str]:
        """
        Identify the critical path through the network.
        
        The critical path consists of tasks with zero slack.
        
        Returns:
            List of task IDs in the critical path
        """
        critical_tasks = [node for node in self.slack_times if self.slack_times[node] == 0]
        
        # Build a subgraph containing only critical tasks
        critical_subgraph = self.graph.subgraph(["start", "end"] + critical_tasks)
        
        # Find the longest path from start to end in the critical subgraph
        try:
            path = nx.shortest_path(critical_subgraph, "start", "end")
            # Remove the start and end nodes
            path = [node for node in path if node not in ("start", "end")]
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            logger.warning("Could not find a complete critical path")
            return critical_tasks
    
    def _calculate_path_duration(self, path: List[str]) -> float:
        """
        Calculate the total duration of a path.
        
        Args:
            path: List of task IDs in the path
            
        Returns:
            Total duration of the path in hours
        """
        return sum(self.graph.nodes[node].get("duration", 0) for node in path)
    
    def _identify_bottlenecks(self) -> List[Dict]:
        """
        Identify potential bottlenecks in the plan.
        
        Bottlenecks are tasks on the critical path with high dependency counts
        or long durations relative to the average.
        
        Returns:
            List of bottleneck tasks with reasons
        """
        bottlenecks = []
        
        if not self.critical_path:
            return bottlenecks
        
        # Calculate average duration of tasks on the critical path
        avg_duration = sum(self.graph.nodes[task_id].get("duration", 0) 
                         for task_id in self.critical_path) / len(self.critical_path)
        
        for task_id in self.critical_path:
            bottleneck_reasons = []
            
            # Check for long duration
            task_duration = self.graph.nodes[task_id].get("duration", 0)
            if task_duration > avg_duration * 1.5:
                bottleneck_reasons.append("Long duration")
            
            # Check for high dependency count
            in_degree = len(list(self.graph.predecessors(task_id)))
            if in_degree > 2:
                bottleneck_reasons.append(f"High dependency count ({in_degree})")
            
            # Check for high dependent count
            out_degree = len(list(self.graph.successors(task_id)))
            if out_degree > 2:
                bottleneck_reasons.append(f"High dependent count ({out_degree})")
            
            if bottleneck_reasons:
                bottlenecks.append({
                    "task_id": task_id,
                    "reasons": bottleneck_reasons,
                    "duration": task_duration,
                    "dependencies": list(self.graph.predecessors(task_id)),
                    "dependents": list(self.graph.successors(task_id))
                })
        
        return bottlenecks
    
    def _get_task_duration_hours(self, task: Task) -> float:
        """
        Get the duration of a task in hours.
        
        Args:
            task: The task object
            
        Returns:
            Duration in hours
        """
        # Default to hours if unit not specified
        unit = task.duration_unit.lower() if hasattr(task, "duration_unit") else "hours"
        
        # Convert duration to hours based on unit
        if unit in ("hour", "hours", "hr", "hrs"):
            return task.duration
        elif unit in ("day", "days"):
            return task.duration * 8  # Assuming 8-hour workdays
        elif unit in ("week", "weeks"):
            return task.duration * 40  # Assuming 40-hour workweeks
        else:
            logger.warning(f"Unknown duration unit: {unit}, defaulting to hours")
            return task.duration
    
    def visualize(self, filename: str = "critical_path.png") -> str:
        """
        Generate a visualization of the critical path.
        
        Args:
            filename: The filename to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib as mpl
            
            # Create a copy of the graph for visualization
            vis_graph = self.graph.copy()
            
            # Set node positions using a layout algorithm
            pos = nx.nx_agraph.graphviz_layout(vis_graph, prog="dot")
            
            # Create a figure
            plt.figure(figsize=(12, 8))
            
            # Draw non-critical nodes
            non_critical = [node for node in vis_graph.nodes() 
                          if node not in self.critical_path and node not in ("start", "end")]
            nx.draw_networkx_nodes(vis_graph, pos, nodelist=non_critical,
                                 node_color="lightblue", node_size=500)
            
            # Draw critical nodes
            critical = [node for node in vis_graph.nodes() if node in self.critical_path]
            nx.draw_networkx_nodes(vis_graph, pos, nodelist=critical,
                                 node_color="red", node_size=500)
            
            # Draw start and end nodes
            nx.draw_networkx_nodes(vis_graph, pos, nodelist=["start"],
                                 node_color="green", node_size=500)
            nx.draw_networkx_nodes(vis_graph, pos, nodelist=["end"],
                                 node_color="purple", node_size=500)
            
            # Draw edges
            non_critical_edges = [(u, v) for u, v in vis_graph.edges() 
                                if u not in self.critical_path or v not in self.critical_path]
            critical_edges = [(u, v) for u, v in vis_graph.edges() 
                            if u in self.critical_path and v in self.critical_path]
            
            nx.draw_networkx_edges(vis_graph, pos, edgelist=non_critical_edges,
                                 edge_color="gray", width=1)
            nx.draw_networkx_edges(vis_graph, pos, edgelist=critical_edges,
                                 edge_color="red", width=2)
            
            # Draw labels
            nx.draw_networkx_labels(vis_graph, pos)
            
            # Save the figure
            plt.title("Critical Path Analysis")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()
            
            logger.info(f"Visualization saved to {filename}")
            return filename
        except ImportError:
            logger.warning("Visualization requires matplotlib and graphviz")
            return ""
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return ""