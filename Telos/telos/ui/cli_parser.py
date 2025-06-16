"""Command-line argument parser for Telos.

This module provides the argument parser for the Telos CLI.
"""

import argparse
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the Telos CLI.
    
    Returns:
        Argument parser
    """
    parser = argparse.ArgumentParser(description="Telos - Tekton's user interface and requirements manager")
    
    # Add global options
    parser.add_argument("--data-dir", help="Data directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Project commands
    project_parser = subparsers.add_parser("project", help="Project commands")
    project_subparsers = project_parser.add_subparsers(dest="subcommand", help="Project subcommand")
    
    project_create_parser = project_subparsers.add_parser("create", help="Create a project")
    project_create_parser.add_argument("name", help="Project name")
    project_create_parser.add_argument("--description", help="Project description")
    
    project_list_parser = project_subparsers.add_parser("list", help="List projects")
    
    project_show_parser = project_subparsers.add_parser("show", help="Show a project")
    project_show_parser.add_argument("project_id", help="Project ID")
    
    project_delete_parser = project_subparsers.add_parser("delete", help="Delete a project")
    project_delete_parser.add_argument("project_id", help="Project ID")
    
    # Requirement commands
    requirement_parser = subparsers.add_parser("requirement", help="Requirement commands")
    requirement_subparsers = requirement_parser.add_subparsers(dest="subcommand", help="Requirement subcommand")
    
    requirement_add_parser = requirement_subparsers.add_parser("add", help="Add a requirement")
    requirement_add_parser.add_argument("project_id", help="Project ID")
    requirement_add_parser.add_argument("title", help="Requirement title")
    requirement_add_parser.add_argument("--description", help="Requirement description")
    requirement_add_parser.add_argument("--type", dest="requirement_type", default="functional",
                                      help="Requirement type")
    requirement_add_parser.add_argument("--priority", default="medium", 
                                      help="Priority (low, medium, high, critical)")
    requirement_add_parser.add_argument("--tags", help="Tags (comma-separated)")
    requirement_add_parser.add_argument("--parent", dest="parent_id", help="Parent requirement ID")
    requirement_add_parser.add_argument("--interactive", "-i", action="store_true", 
                                     help="Start interactive refinement after adding")
    
    requirement_list_parser = requirement_subparsers.add_parser("list", help="List requirements")
    requirement_list_parser.add_argument("project_id", help="Project ID")
    requirement_list_parser.add_argument("--status", help="Filter by status")
    requirement_list_parser.add_argument("--type", dest="requirement_type", help="Filter by type")
    requirement_list_parser.add_argument("--priority", help="Filter by priority")
    requirement_list_parser.add_argument("--tag", help="Filter by tag")
    
    requirement_show_parser = requirement_subparsers.add_parser("show", help="Show a requirement")
    requirement_show_parser.add_argument("project_id", help="Project ID")
    requirement_show_parser.add_argument("requirement_id", help="Requirement ID")
    
    requirement_update_parser = requirement_subparsers.add_parser("update", help="Update a requirement")
    requirement_update_parser.add_argument("project_id", help="Project ID")
    requirement_update_parser.add_argument("requirement_id", help="Requirement ID")
    requirement_update_parser.add_argument("--title", help="New title")
    requirement_update_parser.add_argument("--description", help="New description")
    requirement_update_parser.add_argument("--type", dest="requirement_type", help="New type")
    requirement_update_parser.add_argument("--priority", help="New priority")
    requirement_update_parser.add_argument("--status", help="New status")
    requirement_update_parser.add_argument("--tags", help="New tags (comma-separated)")
    
    requirement_delete_parser = requirement_subparsers.add_parser("delete", help="Delete a requirement")
    requirement_delete_parser.add_argument("project_id", help="Project ID")
    requirement_delete_parser.add_argument("requirement_id", help="Requirement ID")
    
    # Visualization commands
    viz_parser = subparsers.add_parser("viz", help="Visualization commands")
    viz_subparsers = viz_parser.add_subparsers(dest="subcommand", help="Visualization subcommand")
    
    viz_requirements_parser = viz_subparsers.add_parser("requirements", help="Visualize requirements")
    viz_requirements_parser.add_argument("project_id", help="Project ID")
    viz_requirements_parser.add_argument("--format", default="hierarchy", 
                                       help="Format (hierarchy, graph)")
    viz_requirements_parser.add_argument("--output", help="Output file")
    
    # Refine commands
    refine_parser = subparsers.add_parser("refine", help="Requirement refinement commands")
    refine_subparsers = refine_parser.add_subparsers(dest="subcommand", help="Refinement subcommand")
    
    refine_requirement_parser = refine_subparsers.add_parser("requirement", help="Refine a requirement")
    refine_requirement_parser.add_argument("project_id", help="Project ID")
    refine_requirement_parser.add_argument("--requirement-id", help="Requirement ID (if omitted, create new)")
    
    refine_analyze_parser = refine_subparsers.add_parser("analyze", help="Analyze requirements for planning")
    refine_analyze_parser.add_argument("project_id", help="Project ID")
    
    # Prometheus integration commands
    prometheus_parser = subparsers.add_parser("prometheus", help="Prometheus integration commands")
    prometheus_subparsers = prometheus_parser.add_subparsers(dest="subcommand", help="Prometheus subcommand")
    
    prometheus_plan_parser = prometheus_subparsers.add_parser("plan", help="Create a plan from requirements")
    prometheus_plan_parser.add_argument("project_id", help="Project ID")
    
    # Hermes commands
    hermes_parser = subparsers.add_parser("hermes", help="Hermes commands")
    hermes_subparsers = hermes_parser.add_subparsers(dest="subcommand", help="Hermes subcommand")
    
    hermes_register_parser = hermes_subparsers.add_parser("register", help="Register with Hermes")
    
    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args(args)
