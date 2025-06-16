"""
MCP tool management commands for the Ergon CLI.

This module provides commands for listing, searching, and managing MCP tools
in the Ergon repository.
"""

import typer
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import textwrap

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from ergon.core.repository.repository import RepositoryService
from ergon.core.repository.models import ComponentType
from ergon.core.repository.mcp import get_registered_tools, get_tool

# Create typer app
app = typer.Typer(help="MCP tool management commands")

# Create console
console = Console()

# Configure logger
logger = logging.getLogger(__name__)


@app.command("list")
def list_tools(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter tools by tag"),
    tool_type: Optional[str] = typer.Option(None, "--type", help="Filter by tool type (python, js, mcp, etc.)"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format", 
                                    choices=["text", "json"])
):
    """List MCP tools in the repository."""
    try:
        repo = RepositoryService()
        components = repo.list_components(component_type=ComponentType.TOOL)
        
        # Filter by tag if specified
        if tag:
            filtered_components = []
            for comp in components:
                for capability in comp.capabilities:
                    if capability.name.lower() == tag.lower():
                        filtered_components.append(comp)
                        break
            components = filtered_components
        
        # Filter by tool type if specified
        if tool_type:
            components = [c for c in components if c.implementation_type.lower() == tool_type.lower()]
        
        # Get MCP tools as well
        mcp_tools = get_registered_tools()
        
        if output_format == "json":
            # Convert to JSON-serializable format
            result = []
            for component in components:
                tool_data = {
                    "id": component.id,
                    "name": component.name,
                    "description": component.description,
                    "type": component.implementation_type,
                    "version": component.version,
                    "capabilities": [{"name": c.name, "description": c.description} 
                                    for c in component.capabilities],
                    "parameters": [{"name": p.name, "type": p.type, "description": p.description,
                                   "required": p.required, "default": p.default_value}
                                   for p in component.parameters],
                    "created_at": component.created_at.isoformat() if component.created_at else None,
                    "updated_at": component.updated_at.isoformat() if component.updated_at else None
                }
                result.append(tool_data)
            
            # Include MCP tools that aren't in the DB
            for name, info in mcp_tools.items():
                if not any(c.name == name for c in components):
                    params = []
                    for param_name, param_info in info['schema']['parameters']['properties'].items():
                        params.append({
                            "name": param_name,
                            "type": param_info.get("type", "string"),
                            "description": param_info.get("description", ""),
                            "required": param_name in info['schema']['parameters'].get('required', []),
                            "default": param_info.get("default", None)
                        })
                    
                    tool_data = {
                        "id": None,
                        "name": name,
                        "description": info["description"],
                        "type": "mcp",
                        "version": info["version"],
                        "capabilities": [{"name": tag, "description": ""} for tag in info["tags"]],
                        "parameters": params,
                        "created_at": None,
                        "updated_at": None
                    }
                    result.append(tool_data)
            
            console.print(json.dumps(result, indent=2))
        else:
            # Text output
            if not components and not mcp_tools:
                console.print("No tools found.")
                return
            
            console.print("\n[bold]MCP Tools in Repository:[/bold]")
            console.print("=========================")
            
            for component in components:
                if component.implementation_type != "mcp":
                    continue
                    
                console.print(f"\n[bold blue]{component.name}[/bold blue] (v{component.version})")
                console.print(f"[dim]Description:[/dim] {component.description}")
                
                if component.capabilities:
                    console.print("[dim]Tags:[/dim] " + ", ".join(c.name for c in component.capabilities))
                
                if component.parameters:
                    console.print("[dim]Parameters:[/dim]")
                    for param in component.parameters:
                        required = "[bold red](Required)[/bold red]" if param.required else "[dim](Optional)[/dim]"
                        default = f", default={param.default_value}" if param.default_value else ""
                        console.print(f"  • {param.name}: {param.type} {required}{default}")
                        if param.description:
                            for line in textwrap.wrap(param.description, width=70):
                                console.print(f"    [dim]{line}[/dim]")
            
            # Show MCP tools that aren't in the DB
            for name, info in mcp_tools.items():
                if not any(c.name == name for c in components):
                    console.print(f"\n[bold blue]{name}[/bold blue] (v{info['version']})")
                    console.print(f"[dim]Description:[/dim] {info['description']}")
                    
                    if info["tags"]:
                        console.print("[dim]Tags:[/dim] " + ", ".join(info["tags"]))
                    
                    if 'properties' in info['schema']['parameters']:
                        console.print("[dim]Parameters:[/dim]")
                        for param_name, param_info in info['schema']['parameters']['properties'].items():
                            required = "[bold red](Required)[/bold red]" if param_name in info['schema']['parameters'].get('required', []) else "[dim](Optional)[/dim]"
                            default = f", default={param_info.get('default')}" if 'default' in param_info else ""
                            console.print(f"  • {param_name}: {param_info.get('type', 'string')} {required}{default}")
                            if 'description' in param_info:
                                for line in textwrap.wrap(param_info['description'], width=70):
                                    console.print(f"    [dim]{line}[/dim]")
    
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command("show")
def show_tool(
    name: str = typer.Argument(..., help="Name of the tool to display"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format", 
                                     choices=["text", "json"])
):
    """Show details of a specific MCP tool."""
    try:
        # Try to get from MCP registry first (more detailed info)
        mcp_tool = get_tool(name)
        
        # Also try to get from repository (might have additional metadata)
        repo = RepositoryService()
        repo_tool = repo.get_component_by_name(name)
        
        if not mcp_tool and not repo_tool:
            console.print(f"[bold red]Tool '{name}' not found.[/bold red]")
            return
        
        if output_format == "json":
            result = {}
            
            # Start with repo data if available
            if repo_tool:
                result = {
                    "id": repo_tool.id,
                    "name": repo_tool.name,
                    "description": repo_tool.description,
                    "type": repo_tool.implementation_type,
                    "version": repo_tool.version,
                    "capabilities": [{"name": c.name, "description": c.description} 
                                   for c in repo_tool.capabilities],
                    "parameters": [{"name": p.name, "type": p.type, "description": p.description,
                                   "required": p.required, "default": p.default_value}
                                  for p in repo_tool.parameters],
                    "created_at": repo_tool.created_at.isoformat() if repo_tool.created_at else None,
                    "updated_at": repo_tool.updated_at.isoformat() if repo_tool.updated_at else None
                }
            
            # Add/override with MCP data if available
            if mcp_tool:
                if not result:
                    result = {
                        "id": None,
                        "name": mcp_tool["name"],
                        "created_at": None,
                        "updated_at": None
                    }
                
                result.update({
                    "description": mcp_tool["description"],
                    "type": "mcp",
                    "version": mcp_tool["version"],
                    "schema": mcp_tool["schema"],
                    "tags": mcp_tool["tags"],
                    "metadata": mcp_tool["metadata"]
                })
                
                # Add parameters from schema
                params = []
                if "properties" in mcp_tool["schema"]["parameters"]:
                    for param_name, param_info in mcp_tool["schema"]["parameters"]["properties"].items():
                        params.append({
                            "name": param_name,
                            "type": param_info.get("type", "string"),
                            "description": param_info.get("description", ""),
                            "required": param_name in mcp_tool["schema"]["parameters"].get("required", []),
                            "default": param_info.get("default", None)
                        })
                
                result["parameters"] = params
            
            console.print(json.dumps(result, indent=2))
        else:
            # Text output - combine information from both sources
            if mcp_tool:
                panel = Panel(
                    f"[bold blue]{mcp_tool['name']}[/bold blue] (v{mcp_tool['version']})\n\n"
                    f"[dim]Type:[/dim] mcp\n"
                    f"[dim]Description:[/dim] {mcp_tool['description']}",
                    title="Tool Details",
                    expand=False
                )
                console.print(panel)
                
                if mcp_tool["tags"]:
                    console.print("[bold]Tags:[/bold]")
                    for tag in mcp_tool["tags"]:
                        console.print(f"  • {tag}")
                    console.print()
                
                if mcp_tool["metadata"]:
                    console.print("[bold]Metadata:[/bold]")
                    for key, value in mcp_tool["metadata"].items():
                        console.print(f"  • {key}: {value}")
                    console.print()
                
                if "properties" in mcp_tool["schema"]["parameters"]:
                    console.print("[bold]Parameters:[/bold]")
                    for param_name, param_info in mcp_tool["schema"]["parameters"]["properties"].items():
                        required = "[bold red](Required)[/bold red]" if param_name in mcp_tool["schema"]["parameters"].get("required", []) else "[dim](Optional)[/dim]"
                        default = f", default={param_info.get('default')}" if "default" in param_info else ""
                        console.print(f"  • {param_name}: {param_info.get('type', 'string')} {required}{default}")
                        if "description" in param_info:
                            for line in textwrap.wrap(param_info["description"], width=70):
                                console.print(f"    [dim]{line}[/dim]")
            elif repo_tool:
                panel = Panel(
                    f"[bold blue]{repo_tool.name}[/bold blue] (v{repo_tool.version})\n\n"
                    f"[dim]Type:[/dim] {repo_tool.implementation_type}\n"
                    f"[dim]Description:[/dim] {repo_tool.description}",
                    title="Tool Details",
                    expand=False
                )
                console.print(panel)
                
                if repo_tool.capabilities:
                    console.print("[bold]Tags:[/bold]")
                    for cap in repo_tool.capabilities:
                        console.print(f"  • {cap.name}")
                        if cap.description:
                            console.print(f"    [dim]{cap.description}[/dim]")
                    console.print()
                
                if repo_tool.parameters:
                    console.print("[bold]Parameters:[/bold]")
                    for param in repo_tool.parameters:
                        required = "[bold red](Required)[/bold red]" if param.required else "[dim](Optional)[/dim]"
                        default = f", default={param.default_value}" if param.default_value else ""
                        console.print(f"  • {param.name}: {param.type} {required}{default}")
                        if param.description:
                            for line in textwrap.wrap(param.description, width=70):
                                console.print(f"    [dim]{line}[/dim]")
    
    except Exception as e:
        logger.error(f"Error showing tool: {str(e)}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command("search")
def search_tools(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format", 
                                     choices=["text", "json"])
):
    """Search for MCP tools by keyword."""
    try:
        repo = RepositoryService()
        results = repo.search_components(query, component_type=ComponentType.TOOL, limit=limit)
        
        # Filter for MCP tools
        results = [(comp, score) for comp, score in results if comp.implementation_type == "mcp"]
        
        if not results:
            console.print("No MCP tools found matching the query.")
            return
        
        if output_format == "json":
            json_results = []
            for component, score in results:
                tool_data = {
                    "id": component.id,
                    "name": component.name,
                    "description": component.description,
                    "type": component.implementation_type,
                    "version": component.version,
                    "relevance_score": score,
                    "capabilities": [{"name": c.name, "description": c.description} 
                                   for c in component.capabilities],
                    "parameters": [{"name": p.name, "type": p.type, "description": p.description,
                                   "required": p.required, "default": p.default_value}
                                  for p in component.parameters]
                }
                json_results.append(tool_data)
            
            console.print(json.dumps(json_results, indent=2))
        else:
            console.print(f"\n[bold]Search results for '{query}':[/bold]")
            
            for component, score in results:
                console.print(f"\n[bold blue]{component.name}[/bold blue] (relevance: {score:.2f})")
                console.print(f"[dim]Type:[/dim] {component.implementation_type}")
                console.print(f"[dim]Description:[/dim] {component.description}")
                
                if component.capabilities:
                    console.print("[dim]Tags:[/dim] " + ", ".join(c.name for c in component.capabilities))
    
    except Exception as e:
        logger.error(f"Error searching tools: {str(e)}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


if __name__ == "__main__":
    app()