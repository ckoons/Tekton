"""
Tool generation commands for the Ergon CLI.
"""

import os
import json
import asyncio
import logging
from typing import Optional, List
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from ergon.core.repository.tool_generator import generate_tool
from ergon.core.repository.repository import RepositoryService
from ergon.utils.config.settings import settings

# Create typer app
app = typer.Typer(help="Tool generation commands")

# Create console
console = Console()

# Create repository service
repo_service = RepositoryService()

# Configure logger
logger = logging.getLogger(__name__)


@app.command("generate")
def generate_new_tool(
    name: str = typer.Argument(..., help="Tool name"),
    description: str = typer.Argument(..., help="Tool description"),
    output_dir: str = typer.Option(None, "--output", "-o", help="Output directory for generated files"),
    implementation_type: str = typer.Option("python", "--type", "-t", help="Implementation type (python, js, typescript, bash)"),
    add_to_repo: bool = typer.Option(True, "--add-repo/--no-add-repo", help="Add to repository after generation"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use for generation"),
    temperature: float = typer.Option(0.7, "--temperature", help="Temperature for generation"),
    capabilities_file: str = typer.Option(None, "--capabilities", "-c", help="JSON file with capabilities"),
    parameters_file: str = typer.Option(None, "--parameters", "-p", help="JSON file with parameters")
):
    """
    Generate a new tool using AI.
    """
    # Load capabilities if provided
    capabilities = None
    if capabilities_file:
        if not os.path.exists(capabilities_file):
            console.print(f"[bold red]Error:[/bold red] Capabilities file not found: {capabilities_file}")
            return
        
        with open(capabilities_file, "r") as f:
            capabilities = json.load(f)
    
    # Load parameters if provided
    parameters = None
    if parameters_file:
        if not os.path.exists(parameters_file):
            console.print(f"[bold red]Error:[/bold red] Parameters file not found: {parameters_file}")
            return
        
        with open(parameters_file, "r") as f:
            parameters = json.load(f)
    
    # Generate tool
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Generating tool...", total=1)
        
        # Generate tool
        tool_data = generate_tool(
            name=name,
            description=description,
            implementation_type=implementation_type,
            capabilities=capabilities,
            parameters=parameters,
            model_name=model,
            temperature=temperature
        )
        
        progress.update(task, advance=1)
    
    # Output files if requested
    if output_dir:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Write files
        for file in tool_data["files"]:
            file_path = os.path.join(output_dir, file["filename"])
            with open(file_path, "w") as f:
                f.write(file["content"])
        
        console.print(f"[green]Tool files written to:[/green] {output_dir}")
    
    # Add to repository if requested
    if add_to_repo:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Adding tool to repository...", total=1)
            
            # Create tool in repository
            tool_id = repo_service.create_tool(
                name=tool_data["name"],
                description=tool_data["description"],
                implementation_type=tool_data["implementation_type"],
                entry_point=tool_data["entry_point"]
            )
            
            # Add capabilities
            for capability in tool_data["capabilities"]:
                repo_service.add_capability(
                    component_id=tool_id,
                    name=capability["name"],
                    description=capability["description"]
                )
            
            # Add parameters
            for parameter in tool_data["parameters"]:
                repo_service.add_parameter(
                    component_id=tool_id,
                    name=parameter["name"],
                    description=parameter["description"],
                    param_type=parameter.get("type", "string"),
                    required=parameter.get("required", False),
                    default_value=parameter.get("default_value")
                )
            
            # Add files
            for file in tool_data["files"]:
                repo_service.add_file(
                    component_id=tool_id,
                    filename=file["filename"],
                    content=file["content"],
                    file_type=file["file_type"]
                )
            
            progress.update(task, advance=1)
        
        console.print(f"[green]Tool added to repository.[/green] ID: {tool_id}")
    
    # Display summary
    console.print("\n[bold]Tool Generation Summary[/bold]")
    console.print(f"Name: {tool_data['name']}")
    console.print(f"Implementation Type: {tool_data['implementation_type']}")
    console.print(f"Entry Point: {tool_data['entry_point']}")
    
    # Display capabilities
    if tool_data["capabilities"]:
        console.print("\n[bold]Capabilities:[/bold]")
        for capability in tool_data["capabilities"]:
            console.print(f"- {capability['name']}: {capability['description']}")
    
    # Display parameters
    if tool_data["parameters"]:
        console.print("\n[bold]Parameters:[/bold]")
        for parameter in tool_data["parameters"]:
            required = "Required" if parameter.get("required", False) else "Optional"
            default = f" (default: {parameter.get('default_value')})" if "default_value" in parameter and parameter["default_value"] is not None else ""
            console.print(f"- {parameter['name']} ({parameter.get('type', 'string')}, {required}){default}: {parameter['description']}")
    
    # Display file list
    console.print("\n[bold]Generated Files:[/bold]")
    for file in tool_data["files"]:
        console.print(f"- {file['filename']} ({file['file_type']})")


@app.command("view")
def view_tool(
    tool_id: int = typer.Argument(..., help="Tool ID to view"),
    show_files: bool = typer.Option(False, "--files", "-f", help="Show file contents")
):
    """
    View details of a tool.
    """
    # Get tool from repository
    tool = repo_service.get_component(tool_id)
    
    if not tool or tool.type != "tool":
        console.print("[bold red]Error:[/bold red] Tool not found.")
        return
    
    # Display tool details
    console.print(f"[bold]Tool: {tool.name}[/bold] (ID: {tool.id})")
    console.print(f"Description: {tool.description}")
    console.print(f"Version: {tool.version}")
    console.print(f"Implementation Type: {tool.implementation_type}")
    console.print(f"Entry Point: {tool.entry_point}")
    
    # Display capabilities
    if tool.capabilities:
        console.print("\n[bold]Capabilities:[/bold]")
        for capability in tool.capabilities:
            console.print(f"- {capability.name}: {capability.description}")
    
    # Display parameters
    if tool.parameters:
        console.print("\n[bold]Parameters:[/bold]")
        for parameter in tool.parameters:
            required = "Required" if parameter.required else "Optional"
            default = f" (default: {parameter.default_value})" if parameter.default_value else ""
            console.print(f"- {parameter.name} ({parameter.type}, {required}){default}: {parameter.description}")
    
    # Display files
    if tool.files:
        console.print("\n[bold]Files:[/bold]")
        for file in tool.files:
            console.print(f"- {file.filename} ({file.content_type})")
            
            # Show file contents if requested
            if show_files:
                syntax = Syntax(
                    file.content,
                    lexer_name=_get_lexer_for_file(file.filename),
                    theme="monokai",
                    line_numbers=True,
                    word_wrap=True
                )
                console.print(f"\n[bold]{file.filename}:[/bold]")
                console.print(syntax)
                console.print("")


@app.command("extract-capabilities")
def extract_capabilities(
    tool_id: int = typer.Argument(..., help="Tool ID to extract capabilities from"),
    output_file: str = typer.Option(None, "--output", "-o", help="Output file for capabilities JSON")
):
    """
    Extract capabilities from an existing tool.
    """
    # Get tool from repository
    tool = repo_service.get_component(tool_id)
    
    if not tool or tool.type != "tool":
        console.print("[bold red]Error:[/bold red] Tool not found.")
        return
    
    # Extract capabilities
    capabilities = [
        {
            "name": capability.name,
            "description": capability.description
        }
        for capability in tool.capabilities
    ]
    
    # Output capabilities
    if output_file:
        with open(output_file, "w") as f:
            json.dump(capabilities, f, indent=2)
        console.print(f"[green]Capabilities written to:[/green] {output_file}")
    else:
        console.print(json.dumps(capabilities, indent=2))


@app.command("extract-parameters")
def extract_parameters(
    tool_id: int = typer.Argument(..., help="Tool ID to extract parameters from"),
    output_file: str = typer.Option(None, "--output", "-o", help="Output file for parameters JSON")
):
    """
    Extract parameters from an existing tool.
    """
    # Get tool from repository
    tool = repo_service.get_component(tool_id)
    
    if not tool or tool.type != "tool":
        console.print("[bold red]Error:[/bold red] Tool not found.")
        return
    
    # Extract parameters
    parameters = [
        {
            "name": parameter.name,
            "description": parameter.description,
            "type": parameter.type,
            "required": parameter.required,
            "default_value": parameter.default_value
        }
        for parameter in tool.parameters
    ]
    
    # Output parameters
    if output_file:
        with open(output_file, "w") as f:
            json.dump(parameters, f, indent=2)
        console.print(f"[green]Parameters written to:[/green] {output_file}")
    else:
        console.print(json.dumps(parameters, indent=2))


def _get_lexer_for_file(filename: str) -> str:
    """Get Pygments lexer for file."""
    ext = os.path.splitext(filename)[1].lower()
    
    lexers = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".sh": "bash",
        ".md": "markdown",
        ".json": "json",
        ".txt": "text",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".env": "ini"
    }
    
    return lexers.get(ext, "text")


if __name__ == "__main__":
    app()