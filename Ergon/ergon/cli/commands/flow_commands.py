"""
Ergon CLI - Flow Commands

Contains commands for running flows with multiple agents.
"""

import typer
from rich.console import Console
import asyncio
from typing import List, Optional

from ergon.utils.config.settings import settings
from ergon.core.database.engine import init_db
from ergon.cli.utils.db_helpers import ensure_db_initialized

# Initialize console for rich output
console = Console()

def run_flow_command(
    prompt: str = typer.Argument(..., help="The prompt to run the flow with"),
    flow_type: str = typer.Option("planning", "--type", "-t", help="Flow type (planning, simple)"),
    agent_names: List[str] = typer.Option([], "--agent", "-a", help="Agent names to include in the flow"),
    max_steps: int = typer.Option(30, "--max-steps", "-m", help="Maximum number of steps for planning flow"),
    timeout: Optional[int] = typer.Option(None, "--timeout", help="Timeout in seconds for flow execution"),
):
    """Run a flow with multiple agents for complex tasks."""
    try:
        from ergon.core.agents.runner import AgentRunner
        from ergon.core.database.engine import get_db_session
        from ergon.core.database.models import Agent as DatabaseAgent
        from ergon.core.flow.factory import FlowFactory
        from ergon.core.flow.types import FlowType
        
        # Initialize database if not exists
        ensure_db_initialized()
        
        # Load the specified agents
        agents = {}
        with get_db_session() as db:
            if agent_names:
                # Use specified agents
                for agent_name in agent_names:
                    # Try by ID first, then name
                    try:
                        agent_id = int(agent_name)
                        agent = db.query(DatabaseAgent).filter(DatabaseAgent.id == agent_id).first()
                    except ValueError:
                        agent = db.query(DatabaseAgent).filter(DatabaseAgent.name == agent_name).first()
                        
                    if not agent:
                        # Try partial name match
                        agent = db.query(DatabaseAgent).filter(DatabaseAgent.name.ilike(f"%{agent_name}%")).first()
                        
                    if agent:
                        # Create agent runner
                        runner = AgentRunner(agent=agent, timeout=timeout)
                        agents[agent.name.lower()] = runner
                    else:
                        console.print(f"[bold red]Agent '{agent_name}' not found.[/bold red]")
            else:
                # No agents specified, get all agents
                all_agents = db.query(DatabaseAgent).all()
                if all_agents:
                    for agent in all_agents:
                        runner = AgentRunner(agent=agent, timeout=timeout)
                        agents[agent.name.lower()] = runner
                
        if not agents:
            console.print("[bold red]No agents available. Create agents first with 'ergon create'.[/bold red]")
            raise typer.Exit(1)
            
        # Create flow
        try:
            flow_enum = FlowType(flow_type.lower())
        except ValueError:
            console.print(f"[bold red]Invalid flow type: {flow_type}. Valid types: planning, simple[/bold red]")
            raise typer.Exit(1)
            
        flow = FlowFactory.create_flow(
            flow_type=flow_enum,
            agents=agents,
            max_steps=max_steps
        )
        
        # Execute flow
        with console.status(f"[bold green]Running {flow_type} flow with {len(agents)} agents..."):
            result = asyncio.run(flow.execute(prompt))
            
        console.print("[bold green]Flow execution complete![/bold green]\n")
        console.print(result)
        
    except Exception as e:
        console.print(f"[bold red]Error running flow: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        raise typer.Exit(1)