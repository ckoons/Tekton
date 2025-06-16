"""
Ergon CLI - Agent Commands

Contains commands for creating, listing, running, and deleting agents.
"""

import typer
from rich.console import Console
from rich.table import Table
import os
import json
import asyncio
from datetime import datetime
from typing import Optional

from ergon.utils.config.settings import settings
from ergon.core.database.engine import init_db, get_db_session
from ergon.core.database.models import Agent as DatabaseAgent
from ergon.cli.utils.db_helpers import ensure_db_initialized
from ergon.cli.utils.agent_finder import find_agent_by_identifier

# Initialize console for rich output
console = Console()

def create_agent(
    name: str = typer.Option(..., "--name", "-n", help="Name for the agent"),
    description: str = typer.Option(None, "--description", "-d", help="Description for the agent"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use (defaults to settings)"),
    agent_type: str = typer.Option("standard", "--type", "-t", help="Type of agent to create (standard, github, mail, browser)"),
):
    """Create a new AI agent with the given specifications."""
    try:
        from ergon.core.agents.generator import AgentGenerator, generate_agent
        from ergon.core.database.engine import get_db_session
        from ergon.core.database.models import Agent as DatabaseAgent, AgentFile, AgentTool
        
        # Initialize database if not exists
        ensure_db_initialized()
        
        # Set model if not specified
        if not model:
            model = settings.default_model
        
        # Validate model
        if model not in settings.available_models:
            available = "\n".join([f"  - {m}" for m in settings.available_models])
            console.print(f"[bold red]Model '{model}' not available. Available models:[/bold red]\n{available}")
            raise typer.Exit(1)
        
        # Validate agent type
        valid_types = ["standard", "github", "mail", "browser", "nexus"]
        if agent_type not in valid_types:
            console.print(f"[bold red]Invalid agent type: {agent_type}. Valid types: {', '.join(valid_types)}[/bold red]")
            raise typer.Exit(1)
        
        # Check if creating GitHub agent and validate requirements
        if agent_type == "github" and not settings.has_github:
            console.print("[bold yellow]Warning: GitHub API token not configured.[/bold yellow]")
            console.print("Set GITHUB_API_TOKEN and GITHUB_USERNAME in your .env file for GitHub agent to work.")
            
            if not typer.confirm("Continue anyway?"):
                raise typer.Exit(0)
        
        # Create agent
        with console.status(f"[bold green]Creating {agent_type} agent '{name}'..."):
            # Generate agent data
            agent_data = generate_agent(
                name=name,
                description=description or f"An AI assistant named {name}",
                model_name=model,
                agent_type=agent_type
            )
            
            # Save agent to database
            with get_db_session() as db:
                agent = DatabaseAgent(
                    name=agent_data["name"],
                    description=agent_data["description"],
                    model_name=model,
                    system_prompt=agent_data["system_prompt"]
                )
                db.add(agent)
                db.commit()
                db.refresh(agent)
                
                # Save agent files
                for file_data in agent_data["files"]:
                    file = AgentFile(
                        agent_id=agent.id,
                        filename=file_data["filename"],
                        file_type=file_data["file_type"],
                        content=file_data["content"]
                    )
                    db.add(file)
                
                # Save agent tools
                for tool_data in agent_data["tools"]:
                    # For GitHub agent, function_def may already be a string
                    function_def = tool_data["function_def"]
                    if not isinstance(function_def, str):
                        function_def = json.dumps(function_def)
                    
                    tool = AgentTool(
                        agent_id=agent.id,
                        name=tool_data["name"],
                        description=tool_data["description"],
                        function_def=function_def
                    )
                    db.add(tool)
                
                db.commit()
                # Store ID before closing session
                agent_id = agent.id
        
        console.print(f"[bold green]{agent_type.capitalize()} agent '{name}' created successfully with ID {agent_id}![/bold green]")
        
        # Special instructions for different agent types
        if agent_type == "github":
            console.print("\n[bold cyan]GitHub Agent Setup Instructions:[/bold cyan]")
            console.print("1. Make sure you have a GitHub personal access token with appropriate permissions")
            console.print("2. Set these environment variables in your .env file:")
            console.print("   - GITHUB_API_TOKEN=your_token_here")
            console.print("   - GITHUB_USERNAME=your_username_here\n")
            console.print(f"Run the agent with: [bold]ergon run {agent_id} --interactive[/bold]")
        elif agent_type == "mail":
            console.print("\n[bold cyan]Mail Agent Setup Instructions:[/bold cyan]")
            console.print("1. When you first run the agent, it will guide you through OAuth authentication")
            console.print("2. You'll need to complete the authentication process in your web browser")
            console.print("3. For Gmail:")
            console.print("   - Go to console.cloud.google.com and create a project")
            console.print("   - Enable the Gmail API")
            console.print("   - Create OAuth credentials (Desktop application type)")
            console.print("   - Download the credentials.json file")
            console.print("   - Place it in your config directory as 'gmail_credentials.json'")
            console.print("4. For Outlook/Microsoft 365:")
            console.print("   - Go to portal.azure.com and register a new application")
            console.print("   - Add Microsoft Graph permissions for Mail.Read and Mail.Send")
            console.print("   - Configure authentication with a redirect URI")
            console.print("   - Create a client secret (or use public client flow)")
            console.print("   - Set OUTLOOK_CLIENT_ID in your .env file\n")
            console.print(f"Run the agent with: [bold]ergon run {agent_id} --interactive[/bold]")
        elif agent_type == "browser":
            console.print("\n[bold cyan]Browser Agent Setup Instructions:[/bold cyan]")
            console.print("1. Make sure you have the necessary dependencies installed:")
            console.print("   - browser-use: pip install browser-use==0.1.40")
            console.print("   - playwright: pip install playwright==1.49.1")
            console.print("2. Install browser binaries: playwright install")
            console.print("3. For headless mode control, set in your .env file:")
            console.print("   - BROWSER_HEADLESS=true (or false for visible browser)")
            console.print("4. For screenshots, they'll be saved to ~/ergon_screenshots by default\n")
            console.print(f"Run the agent with: [bold]ergon run {agent_id} --interactive[/bold]")
        
    except Exception as error:
        console.print(f"[bold red]Error creating agent: {str(error)}[/bold red]")
        import traceback
        console.print(f"[dim red]{traceback.format_exc()}[/dim red]")
        raise typer.Exit(1)


def list_agents():
    """List all available agents."""
    try:
        # Initialize database if not exists
        ensure_db_initialized()
        
        # List agents
        with get_db_session() as db:
            agents = db.query(DatabaseAgent).all()
            
            if not agents:
                console.print("[yellow]No agents found. Create one with 'ergon create'.[/yellow]")
                return
            
            table = Table(title="Available Agents")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Description", style="blue")
            table.add_column("Model", style="yellow")
            table.add_column("Created", style="magenta")
            
            for agent in agents:
                table.add_row(
                    str(agent.id),
                    agent.name,
                    agent.description or "",
                    agent.model_name,
                    agent.created_at.strftime("%Y-%m-%d %H:%M") if agent.created_at else ""
                )
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error listing agents: {str(e)}[/bold red]")
        raise typer.Exit(1)


def run_agent(
    agent_identifier: str = typer.Argument(..., help="Name or ID of the agent to run"),
    input: str = typer.Option(None, "--input", "-i", help="Input to send to the agent"),
    interactive: bool = typer.Option(False, "--interactive", help="Run in interactive mode"),
    timeout: Optional[int] = typer.Option(None, "--timeout", "-t", help="Timeout in seconds for agent execution"),
    timeout_action: str = typer.Option("log", "--timeout-action", "-a", help="Action on timeout: log, alarm, or kill"),
):
    """Run an AI agent with the given input."""
    try:
        from ergon.core.agents.runner import AgentRunner
        from ergon.core.database.models import AgentExecution, AgentMessage
        
        # Initialize database if not exists
        ensure_db_initialized()
        
        # Get agent by ID or name
        with get_db_session() as db:
            agent = find_agent_by_identifier(db, agent_identifier)
            
            if not agent:
                # If not found, exit
                raise typer.Exit(1)
            
            # Create execution record
            execution = AgentExecution(agent_id=agent.id)
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # Initialize runner with timeout if specified
            runner = AgentRunner(
                agent=agent, 
                execution_id=execution.id,
                timeout=timeout,
                timeout_action=timeout_action
            )
            
            if interactive:
                # Interactive mode
                console.print(f"[bold green]Running agent '[bold cyan]{agent.name}[/bold cyan]' (ID: {agent.id}) in interactive mode. Type 'exit' to quit.[/bold green]")
                
                while True:
                    user_input = console.input("[bold blue]> [/bold blue]")
                    
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    
                    # Record user message
                    message = AgentMessage(
                        execution_id=execution.id,
                        role="user",
                        content=user_input
                    )
                    db.add(message)
                    db.commit()
                    
                    # Run agent
                    with console.status("[bold green]Agent thinking..."):
                        response = asyncio.run(runner.run(user_input))
                    
                    # Print response with consistent agent name display
                    console.print(f"[bold cyan]{agent.name}[/bold cyan] [dim](ID: {agent.id})[/dim]: {response}")
                    
                    # Record assistant message
                    message = AgentMessage(
                        execution_id=execution.id,
                        role="assistant",
                        content=response
                    )
                    db.add(message)
                    db.commit()
                
                # Mark execution as completed
                execution.completed_at = datetime.now()
                execution.success = True
                db.commit()
                
            elif input:
                # Run with provided input
                with console.status(f"[bold green]Running agent '{agent.name}'..."):
                    # Record user message
                    message = AgentMessage(
                        execution_id=execution.id,
                        role="user",
                        content=input
                    )
                    db.add(message)
                    db.commit()
                    
                    # Run agent
                    response = asyncio.run(runner.run(input))
                    
                    # Record assistant message
                    message = AgentMessage(
                        execution_id=execution.id,
                        role="assistant",
                        content=response
                    )
                    db.add(message)
                    
                    # Mark execution as completed
                    execution.completed_at = datetime.now()
                    execution.success = True
                    db.commit()
                
                # Print response with consistent agent name display
                console.print(f"[bold cyan]{agent.name}[/bold cyan] [dim](ID: {agent.id})[/dim]: {response}")
                
            else:
                console.print("[yellow]No input provided. Use --input or --interactive.[/yellow]")
                db.delete(execution)
                db.commit()
        
    except Exception as e:
        console.print(f"[bold red]Error running agent: {str(e)}[/bold red]")
        raise typer.Exit(1)


def delete_agent(
    agent_identifier: str = typer.Argument(..., help="Name or ID of the agent to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation"),
):
    """Delete an AI agent and associated data."""
    try:
        from ergon.core.database.models import AgentFile, AgentTool, AgentExecution, AgentMessage
        
        # Initialize database if not exists
        ensure_db_initialized()
        
        # Get agent by ID or name
        with get_db_session() as db:
            agent = find_agent_by_identifier(db, agent_identifier)
            
            if not agent:
                # If not found, exit
                raise typer.Exit(1)
            
            # Confirm deletion
            if not force:
                console.print(f"[bold yellow]Are you sure you want to delete agent '{agent.name}' (ID: {agent.id})?[/bold yellow]")
                console.print(f"Description: {agent.description}")
                console.print(f"Model: {agent.model_name}")
                if not typer.confirm("Delete this agent?"):
                    console.print("[yellow]Deletion cancelled.[/yellow]")
                    raise typer.Exit(0)
            
            # Store agent info before deletion
            agent_name = agent.name
            agent_id_val = agent.id
            
            # Count related records
            tool_count = db.query(AgentTool).filter(AgentTool.agent_id == agent_id_val).count()
            file_count = db.query(AgentFile).filter(AgentFile.agent_id == agent_id_val).count()
            execution_count = db.query(AgentExecution).filter(AgentExecution.agent_id == agent_id_val).count()
            
            # Start deletion with status
            with console.status(f"[bold red]Deleting agent '{agent_name}' and associated data..."):
                # First delete messages (due to foreign key constraints)
                execution_ids = [row[0] for row in db.query(AgentExecution.id).filter(AgentExecution.agent_id == agent_id_val).all()]
                if execution_ids:
                    message_count = db.query(AgentMessage).filter(AgentMessage.execution_id.in_(execution_ids)).delete(synchronize_session=False)
                else:
                    message_count = 0
                
                # Then delete executions
                db.query(AgentExecution).filter(AgentExecution.agent_id == agent_id_val).delete(synchronize_session=False)
                
                # Delete tools and files
                db.query(AgentTool).filter(AgentTool.agent_id == agent_id_val).delete(synchronize_session=False)
                db.query(AgentFile).filter(AgentFile.agent_id == agent_id_val).delete(synchronize_session=False)
                
                # Finally delete the agent
                db.query(DatabaseAgent).filter(DatabaseAgent.id == agent_id_val).delete(synchronize_session=False)
                
                # Commit changes
                db.commit()
            
            # Show deletion summary
            console.print(f"[bold green]Successfully deleted agent '{agent_name}' (ID: {agent_id_val})![/bold green]")
            console.print(f"Removed:")
            console.print(f"- {tool_count} tool definition(s)")
            console.print(f"- {file_count} agent file(s)")
            console.print(f"- {execution_count} execution record(s)")
            console.print(f"- {message_count} message(s)")
        
    except Exception as e:
        console.print(f"[bold red]Error deleting agent: {str(e)}[/bold red]")
        raise typer.Exit(1)