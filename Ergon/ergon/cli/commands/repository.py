"""
CLI commands for the repository management.

This module provides CLI commands for managing the repository of tools,
agents, and workflows.
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import json
import typer
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from ergon.core.repository.models import ComponentType
from ergon.core.repository.repository import RepositoryService
from ergon.core.configuration.wrapper import ConfigurationGenerator

# Setup console
console = Console()

# Create the CLI app
app = typer.Typer(help="Repository management commands")


@app.command("list")
def list_components(
    type: str = typer.Option(None, "--type", "-t", help="Filter by component type (tool, agent, workflow)"),
    active_only: bool = typer.Option(True, "--all", help="Include inactive components", show_default=False),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
):
    """List components in the repository."""
    repo = RepositoryService()
    
    # Convert type string to enum if provided
    component_type = None
    if type:
        try:
            component_type = ComponentType(type.lower())
        except ValueError:
            console.print(f"[bold red]Error:[/] Invalid component type: {type}")
            console.print(f"Valid types: {', '.join([t.value for t in ComponentType])}")
            sys.exit(1)
    
    # Get components
    components = repo.list_components(component_type=component_type, active_only=not active_only)
    
    if format == "json":
        # Output as JSON
        result = [component.to_dict() for component in components]
        console.print(json.dumps(result, indent=2))
    else:
        # Output as table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Version")
        table.add_column("Description")
        table.add_column("Status")
        
        for component in components:
            status = "[green]Active[/]" if component.is_active else "[red]Inactive[/]"
            table.add_row(
                str(component.id),
                component.name,
                component.type,
                component.version,
                component.description[:50] + "..." if len(component.description) > 50 else component.description,
                status
            )
        
        console.print(table)


@app.command("info")
def component_info(
    component: str = typer.Argument(..., help="Component ID or name"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format (rich, json)"),
):
    """Show detailed information about a component."""
    repo = RepositoryService()
    
    # Try to parse as ID first
    try:
        component_id = int(component)
        result = repo.get_component(component_id)
    except ValueError:
        # If not an ID, try by name
        result = repo.get_component_by_name(component)
    
    if not result:
        console.print(f"[bold red]Error:[/] Component not found: {component}")
        sys.exit(1)
    
    if format == "json":
        # Output as JSON
        console.print(json.dumps(result.to_dict(), indent=2))
    else:
        # Output as rich text
        console.print(Panel(f"[bold]{result.name}[/] (ID: {result.id})", style="bold blue"))
        console.print(f"[bold]Type:[/] {result.type}")
        console.print(f"[bold]Version:[/] {result.version}")
        console.print(f"[bold]Status:[/] {'Active' if result.is_active else 'Inactive'}")
        console.print(f"[bold]Created:[/] {result.created_at}")
        console.print(f"[bold]Updated:[/] {result.updated_at}")
        
        console.print("\n[bold]Description:[/]")
        console.print(result.description)
        
        # Show type-specific details
        if result.type == ComponentType.TOOL:
            console.print(f"\n[bold]Implementation Type:[/] {result.implementation_type}")
            console.print(f"[bold]Entry Point:[/] {result.entry_point}")
        elif result.type == ComponentType.AGENT:
            console.print(f"\n[bold]Model:[/] {result.model}")
            console.print(f"[bold]System Prompt:[/]")
            console.print(Panel(result.system_prompt, style="dim"))
        elif result.type == ComponentType.WORKFLOW:
            console.print(f"\n[bold]Workflow Definition:[/]")
            console.print(Syntax(json.dumps(result.definition, indent=2), "json"))
        
        # Show capabilities
        if result.capabilities:
            console.print("\n[bold]Capabilities:[/]")
            for cap in result.capabilities:
                console.print(f"- [bold]{cap.name}:[/] {cap.description}")
        
        # Show parameters
        if result.parameters:
            console.print("\n[bold]Parameters:[/]")
            param_table = Table(show_header=True)
            param_table.add_column("Name")
            param_table.add_column("Type")
            param_table.add_column("Required")
            param_table.add_column("Default")
            param_table.add_column("Description")
            
            for param in result.parameters:
                param_table.add_row(
                    param.name,
                    param.type,
                    "Yes" if param.required else "No",
                    param.default_value or "",
                    param.description
                )
            
            console.print(param_table)
        
        # Show metadata
        if result.metadata:
            console.print("\n[bold]Metadata:[/]")
            for meta in result.metadata:
                console.print(f"- [bold]{meta.key}:[/] {meta.value}")
        
        # Show files
        if result.files:
            console.print("\n[bold]Files:[/]")
            for file in result.files:
                console.print(f"- [bold]{file.filename}[/] ({file.content_type}): {file.path}")


@app.command("search")
def search_components(
    query: str = typer.Argument(..., help="Search query"),
    type: str = typer.Option(None, "--type", "-t", help="Filter by component type (tool, agent, workflow)"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum number of results"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
):
    """Search for components in the repository."""
    repo = RepositoryService()
    
    # Convert type string to enum if provided
    component_type = None
    if type:
        try:
            component_type = ComponentType(type.lower())
        except ValueError:
            console.print(f"[bold red]Error:[/] Invalid component type: {type}")
            console.print(f"Valid types: {', '.join([t.value for t in ComponentType])}")
            sys.exit(1)
    
    # Search components
    results = repo.search_components(query, component_type=component_type, limit=limit)
    
    if format == "json":
        # Output as JSON
        json_results = [
            {
                "component": component.to_dict(),
                "score": score
            }
            for component, score in results
        ]
        console.print(json.dumps(json_results, indent=2))
    else:
        # Output as table
        if not results:
            console.print(f"No components found matching query: {query}")
            return
            
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Version")
        table.add_column("Description")
        table.add_column("Score")
        
        for component, score in results:
            table.add_row(
                str(component.id),
                component.name,
                component.type,
                component.version,
                component.description[:50] + "..." if len(component.description) > 50 else component.description,
                f"{score:.2f}"
            )
        
        console.print(table)


@app.command("configure")
def configure_component(
    component: str = typer.Argument(..., help="Component ID or name"),
    params_file: str = typer.Option(None, "--params", "-p", help="JSON file with parameters"),
    output: str = typer.Option(None, "--output", "-o", help="Output path for the wrapper script"),
):
    """Generate a wrapper script for a component."""
    repo = RepositoryService()
    
    # Try to parse as ID first
    try:
        component_id = int(component)
        result = repo.get_component(component_id)
    except ValueError:
        # If not an ID, try by name
        result = repo.get_component_by_name(component)
    
    if not result:
        console.print(f"[bold red]Error:[/] Component not found: {component}")
        sys.exit(1)
    
    # Load parameters
    params = {}
    if params_file:
        try:
            with open(params_file, "r") as f:
                params = json.load(f)
        except Exception as e:
            console.print(f"[bold red]Error:[/] Failed to load parameters file: {e}")
            sys.exit(1)
    
    # Create output path if provided
    output_path = None
    if output:
        output_path = Path(output)
    
    # Generate wrapper
    generator = ConfigurationGenerator()
    
    try:
        if result.type == ComponentType.TOOL:
            wrapper_path = generator.generate_tool_wrapper(result, params, output_path)
        elif result.type == ComponentType.AGENT:
            wrapper_path = generator.generate_agent_wrapper(result, params, output_path)
        elif result.type == ComponentType.WORKFLOW:
            wrapper_path = generator.generate_workflow_wrapper(result, params, output_path)
        else:
            console.print(f"[bold red]Error:[/] Unsupported component type: {result.type}")
            sys.exit(1)
            
        console.print(f"[bold green]Success:[/] Generated wrapper script at: {wrapper_path}")
        
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to generate wrapper: {e}")
        sys.exit(1)