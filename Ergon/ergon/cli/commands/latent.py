#!/usr/bin/env python3
"""
Latent Reasoning CLI commands for Ergon.

This module provides CLI commands for working with the Latent Space Reflection Framework.
"""

import asyncio
import json
import logging
import os
import sys
import typer
from typing import Optional, List, Dict, Any, Union
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ergon.utils.config.settings import settings

# Create CLI app
app = typer.Typer(help="Latent Reasoning commands")
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ergon.cli.latent")

# Check if latent reasoning is available
try:
    from ergon.core.agents.latent_reasoning import generate_latent_agent
    from ergon.core.agents.latent_runner import run_agent_with_latent_reasoning
    HAS_LATENT_REASONING = True
except ImportError:
    HAS_LATENT_REASONING = False
    logger.warning("Tekton Latent Reasoning Framework not available")


@app.command("create")
def create_latent_agent(
    name: str = typer.Option(..., "--name", "-n", help="Name of the agent"),
    description: str = typer.Option(..., "--description", "-d", help="Description of the agent"),
    agent_type: str = typer.Option("standard", "--type", "-t", help="Type of agent (standard, nexus, github, browser, mail)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use for the agent"),
    temperature: float = typer.Option(0.7, "--temperature", help="Temperature for generation")
):
    """
    Create a new agent with latent reasoning capabilities.
    """
    if not HAS_LATENT_REASONING:
        console.print("[bold red]Latent reasoning is not available.[/]")
        console.print("Please install the Tekton Latent Space Reflection Framework.")
        return
    
    console.print(f"[bold blue]Creating latent reasoning agent: {name}[/]")
    console.print(f"Type: {agent_type}")
    
    try:
        # Import the appropriate generator function
        if agent_type == "nexus":
            from ergon.core.agents.latent_reasoning import generate_latent_nexus_agent as generator
        elif agent_type == "github":
            from ergon.core.agents.latent_reasoning import generate_latent_github_agent as generator
        elif agent_type == "browser":
            from ergon.core.agents.latent_reasoning import generate_latent_browser_agent as generator
        elif agent_type == "mail":
            from ergon.core.agents.latent_reasoning import generate_latent_mail_agent as generator
        else:
            from ergon.core.agents.latent_reasoning import generate_latent_agent as generator
        
        # Generate the agent
        agent_data = generator(
            name=name,
            description=description,
            model_name=model,
            temperature=temperature
        )
        
        # Store in database
        from ergon.core.database.engine import get_db_session
        from ergon.core.database.models import Agent, AgentFile, AgentTool
        
        with get_db_session() as db:
            # Create agent record
            agent = Agent(
                name=name,
                description=description,
                type=agent_type,
                model_name=agent_data["model_name"],
                system_prompt=agent_data["system_prompt"],
                latent_reasoning=True
            )
            db.add(agent)
            db.commit()
            
            # Add files
            for file_data in agent_data.get("files", []):
                file = AgentFile(
                    agent_id=agent.id,
                    filename=file_data["filename"],
                    content=file_data["content"],
                    file_type=file_data.get("file_type", "")
                )
                db.add(file)
            
            # Add tools
            for tool_data in agent_data.get("tools", []):
                tool = AgentTool(
                    agent_id=agent.id,
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    function_def=tool_data.get("function_def", "{}")
                )
                db.add(tool)
            
            db.commit()
        
        console.print(f"[bold green]Successfully created latent reasoning agent: {name} (ID: {agent.id})[/]")
        console.print("Use the following command to run the agent:")
        console.print(f"  [yellow]ergon latent run {agent.id} --input \"Your input here\"[/]")
    
    except Exception as e:
        console.print(f"[bold red]Error creating agent: {str(e)}[/]")


@app.command("run")
def run_latent_agent(
    agent_id_or_name: str = typer.Argument(..., help="ID or name of the agent to run"),
    input: str = typer.Option(..., "--input", "-i", help="Input to send to the agent"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model to use"),
    temperature: float = typer.Option(0.7, "--temperature", help="Temperature for generation"),
    interactive: bool = typer.Option(False, "--interactive", help="Run in interactive mode"),
    timeout: Optional[int] = typer.Option(None, "--timeout", help="Timeout in seconds"),
    timeout_action: str = typer.Option("log", "--timeout-action", help="Action on timeout: log, alarm, kill")
):
    """
    Run an agent with latent reasoning capabilities.
    """
    if not HAS_LATENT_REASONING:
        console.print("[bold red]Latent reasoning is not available.[/]")
        console.print("Please install the Tekton Latent Space Reflection Framework.")
        return
    
    console.print(f"[bold blue]Running agent with latent reasoning: {agent_id_or_name}[/]")
    
    # Run in async mode
    try:
        result = asyncio.run(run_agent_with_latent_reasoning(
            agent_id_or_name=agent_id_or_name,
            input_text=input,
            model_name=model,
            temperature=temperature,
            interactive=interactive,
            timeout=timeout,
            timeout_action=timeout_action
        ))
        
        if "error" in result:
            console.print(f"[bold red]Error: {result['error']}[/]")
            return
        
        # Display result
        console.print("\n[bold green]Agent Response:[/]")
        console.print(Panel(Markdown(result["result"]), expand=False))
        
        # Display execution info
        console.print(f"\n[blue]Execution Time:[/] {result['execution_time']:.2f} seconds")
        console.print(f"[blue]Agent:[/] {result['agent_name']} (ID: {result['agent_id']})")
        console.print(f"[blue]Execution ID:[/] {result['execution_id']}")
        
    except Exception as e:
        console.print(f"[bold red]Error running agent: {str(e)}[/]")


@app.command("visualize")
def visualize_reasoning(
    thought_id: str = typer.Argument(..., help="ID of the thought to visualize"),
    output_dir: str = typer.Option("./visualizations", "--output-dir", help="Directory to save visualization")
):
    """
    Visualize a latent reasoning trace.
    """
    if not HAS_LATENT_REASONING:
        console.print("[bold red]Latent reasoning is not available.[/]")
        console.print("Please install the Tekton Latent Space Reflection Framework.")
        return
    
    try:
        # Import the visualizer
        from tekton.utils.latent_space_visualizer import LatentSpaceVisualizer
        
        # Get the reasoning trace
        # This requires access to the latent space which we may not have directly
        # Instead, we'll need to use an agent's latent space
        
        console.print(f"[bold blue]Visualizing reasoning trace: {thought_id}[/]")
        console.print("[yellow]Note: This requires an active agent with access to the thought.[/]")
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the output file path
        output_file = os.path.join(output_dir, f"thought_{thought_id}.html")
        
        # Here we'd ideally retrieve the thought from the latent space
        # Since we don't have direct access, we'll create a placeholder message
        console.print("[yellow]This feature requires direct access to the agent's latent space.[/]")
        console.print("[yellow]Please use the --visualize flag when running an agent to generate visualizations.[/]")
        
    except Exception as e:
        console.print(f"[bold red]Error visualizing reasoning: {str(e)}[/]")


@app.command("info")
def latent_reasoning_info():
    """
    Show information about the Latent Space Reflection Framework.
    """
    console.print("[bold blue]Tekton Latent Space Reflection Framework[/]")
    
    if not HAS_LATENT_REASONING:
        console.print("[bold red]Latent reasoning is not available.[/]")
        console.print("Please install the Tekton Latent Space Reflection Framework.")
        return
    
    try:
        # Import from tekton core
        from tekton.core.latent_reasoning import LatentReasoningMixin
        
        console.print("\n[green]Latent Reasoning is available and properly integrated.[/]")
        console.print("\n[bold]Core Concepts:[/]")
        console.print("1. Continuous latent space reasoning for iterative thought refinement")
        console.print("2. Automatic complexity analysis to determine when deep reasoning is needed")
        console.print("3. Cross-component insight sharing for collaborative reasoning")
        console.print("4. Visualization tools for reasoning traces")
        
        console.print("\n[bold]Available Commands:[/]")
        console.print("- [yellow]ergon latent create[/]: Create a new agent with latent reasoning")
        console.print("- [yellow]ergon latent run[/]: Run an agent with latent reasoning")
        console.print("- [yellow]ergon latent visualize[/]: Visualize a reasoning trace")
        console.print("- [yellow]ergon latent info[/]: Show this information")
        
    except Exception as e:
        console.print(f"[bold red]Error retrieving latent reasoning info: {str(e)}[/]")


if __name__ == "__main__":
    app()