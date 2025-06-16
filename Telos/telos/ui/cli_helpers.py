"""Helper functions for the Telos CLI.

This module provides utility functions for formatting and displaying
information in the Telos CLI.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


def format_timestamp(timestamp: float) -> str:
    """Format a timestamp as a human-readable date.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted date string
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_status_symbol(status: str) -> str:
    """Get a symbol for a requirement status.
    
    Args:
        status: Requirement status
        
    Returns:
        Status symbol
    """
    symbols = {
        "new": "🆕",
        "accepted": "✅",
        "in-progress": "🔄",
        "completed": "✓",
        "rejected": "❌"
    }
    return symbols.get(status, "•")


def get_priority_symbol(priority: str) -> str:
    """Get a symbol for a requirement priority.
    
    Args:
        priority: Requirement priority
        
    Returns:
        Priority symbol
    """
    symbols = {
        "low": "⬇️",
        "medium": "➡️",
        "high": "⬆️",
        "critical": "🔴"
    }
    return symbols.get(priority, "•")


def visualize_hierarchy(project, output: Optional[str] = None) -> None:
    """Visualize requirements as a hierarchy.
    
    Args:
        project: Project to visualize
        output: Output file
    """
    hierarchy = project.get_requirement_hierarchy()
    
    # Helper function to print a node and its children
    def print_node(node_id: str, level: int = 0) -> None:
        if node_id == "root":
            print(f"Project: {project.name}")
        else:
            requirement = project.get_requirement(node_id)
            if requirement:
                indent = "  " * level
                status_symbol = get_status_symbol(requirement.status)
                priority_symbol = get_priority_symbol(requirement.priority)
                print(f"{indent}{status_symbol} {priority_symbol} {node_id}: {requirement.title}")
        
        for child_id in hierarchy.get(node_id, []):
            print_node(child_id, level + 1)
    
    # Print the hierarchy
    print_node("root")
    
    # Save to file if requested
    if output:
        with open(output, "w") as f:
            f.write(f"Requirement Hierarchy for {project.name}\n")
            f.write(f"=================================\n\n")
            
            # Redirect print output to file
            import sys
            old_stdout = sys.stdout
            sys.stdout = f
            print_node("root")
            sys.stdout = old_stdout
        
        print(f"Saved hierarchy to {output}")


def visualize_graph(project, output: Optional[str] = None) -> None:
    """Visualize requirements as a graph.
    
    Args:
        project: Project to visualize
        output: Output file
    """
    print("Graph visualization requires additional dependencies.")
    print("You can install them with: pip install matplotlib networkx")
    
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        
        # Create a graph
        G = nx.DiGraph()
        
        # Add the project as the root node
        G.add_node("Project", label=project.name, type="project")
        
        # Add requirements as nodes
        for req_id, requirement in project.requirements.items():
            G.add_node(req_id, label=requirement.title, type="requirement",
                     status=requirement.status, priority=requirement.priority)
            
            # Connect to parent
            if requirement.parent_id:
                G.add_edge(requirement.parent_id, req_id)
            else:
                G.add_edge("Project", req_id)
            
            # Add dependencies
            for dep_id in requirement.dependencies:
                if dep_id in project.requirements:
                    G.add_edge(dep_id, req_id, style="dashed")
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightblue", 
                            alpha=0.8, nodelist=["Project"])
        
        # Color requirements by status
        status_colors = {
            "new": "lightgreen",
            "accepted": "green",
            "in-progress": "orange",
            "completed": "blue",
            "rejected": "red"
        }
        
        for status, color in status_colors.items():
            nodelist = [n for n, d in G.nodes(data=True) 
                      if d.get("type") == "requirement" and d.get("status") == status]
            if nodelist:
                nx.draw_networkx_nodes(G, pos, node_size=500, node_color=color,
                                    alpha=0.8, nodelist=nodelist)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        
        # Draw labels
        labels = {n: d.get("label", n) for n, d in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title(f"Requirement Graph for {project.name}")
        plt.axis("off")
        
        # Save or show the graph
        if output:
            plt.savefig(output)
            print(f"Saved graph to {output}")
        else:
            plt.show()
        
    except ImportError:
        print("Could not import required libraries for graph visualization.")
