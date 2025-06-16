"""
Nexus command for interacting with memory-enabled agents.
"""

import asyncio
import typer
from typing import Optional
from datetime import datetime
from rich.console import Console

from ergon.core.agents.runner import AgentRunner
from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent, AgentExecution
from sqlalchemy import func

console = Console()

def nexus_command(
    agent: str,
    input: str = typer.Option(None, "--input", "-i", help="Input to send to the agent"),
    interactive: bool = typer.Option(False, "--interactive", help="Enable interactive mode"),
    disable_memory: bool = typer.Option(False, "--no-memory", help="Disable memory features for simpler operation"),
):
    """
    Chat with a memory-enabled Nexus agent.
    
    Args:
        agent: ID or name of the agent to use
        input: Input to send to the agent (if not using interactive mode)
        interactive: Whether to use interactive mode
    """
    # Find agent by ID or name
    try:
        agent_id = int(agent)
        id_lookup = True
    except ValueError:
        id_lookup = False
    
    with get_db_session() as db:
        if id_lookup:
            # Find by ID
            agent_obj = db.query(Agent).filter(Agent.id == agent_id).first()
        else:
            # Find by name
            agent_obj = db.query(Agent).filter(func.lower(Agent.name) == agent.lower()).first()
            
            # Try partial match if no exact match
            if agent_obj is None:
                agent_obj = db.query(Agent).filter(func.lower(Agent.name).contains(agent.lower())).first()
        
        if agent_obj is None:
            console.print(f"[bold red]Agent not found: {agent}[/bold red]")
            raise typer.Exit(1)
        
        agent_id = agent_obj.id
    
    # Print agent details
    console.print(f"[bold green]Agent:[/bold green] {agent_obj.name} (ID: {agent_id})")
    console.print(f"[bold green]Type:[/bold green] {agent_obj.type or 'standard'}")
    
    # Interactive mode
    if interactive:
        console.print("[bold yellow]Interactive Mode:[/bold yellow] Type 'exit' to quit")
        
        execution_id = None
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Add initial memories
        console.print("[bold yellow]Initializing agent memories...[/bold yellow]")
        
        # Create execution for initialization
        with get_db_session() as db:
            init_execution = AgentExecution(
                agent_id=agent_id,
                started_at=datetime.now()
            )
            db.add(init_execution)
            db.commit()
            init_execution_id = init_execution.id
        
        # Create runner with execution ID
        init_runner = AgentRunner(
            agent=agent_obj,
            execution_id=init_execution_id
        )
        
        # Just run a simple command to initialize the agent
        loop.run_until_complete(init_runner.run("Hello, I am a new user."))
        console.print("[bold green]Memories initialized![/bold green]")
        
        while True:
            try:
                # Get user input
                user_input = input("\n[bold cyan]You:[/bold cyan] ")
                if not user_input.strip():
                    continue
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                
                # Create execution if none exists
                if execution_id is None:
                    with get_db_session() as db:
                        execution = AgentExecution(
                            agent_id=agent_id,
                            started_at=datetime.now()
                        )
                        db.add(execution)
                        db.commit()
                        execution_id = execution.id
                
                # Create runner
                runner = AgentRunner(
                    agent=agent_obj,
                    execution_id=execution_id
                )
                
                # Modify the input if memory is disabled
                if disable_memory:
                    # Run in simple mode for all inputs 
                    with console.status("[bold green]Agent thinking...[/bold green]"):
                        response = loop.run_until_complete(runner._run_simple(user_input))
                else:
                    # Run normal mode with memory
                    with console.status("[bold green]Agent thinking...[/bold green]"):
                        response = loop.run_until_complete(runner.run(user_input))
                
                # Print response
                console.print(f"\n[bold green]{agent_obj.name}:[/bold green] {response}")
                
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
                
                # Create new execution after error
                execution_id = None
        
        # Clean up
        loop.close()
        
    # Single response mode
    elif input:
        try:
            # Create loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize memories
            console.print("[bold yellow]Initializing agent memories...[/bold yellow]")
            
            # Create execution for initialization
            with get_db_session() as db:
                init_execution = AgentExecution(
                    agent_id=agent_id,
                    started_at=datetime.now()
                )
                db.add(init_execution)
                db.commit()
                init_execution_id = init_execution.id
            
            # Create runner with execution ID 
            init_runner = AgentRunner(
                agent=agent_obj,
                execution_id=init_execution_id
            )
            
            # Run a simple command to initialize the agent, using the simple mode to avoid tool errors
            loop.run_until_complete(init_runner._run_simple("Hello, I am a new user."))
            console.print("[bold green]Memories initialized![/bold green]")
            
            # Create execution
            with get_db_session() as db:
                execution = AgentExecution(
                    agent_id=agent_id,
                    started_at=datetime.now()
                )
                db.add(execution)
                db.commit()
                execution_id = execution.id
            
            # Create runner with new execution ID
            runner = AgentRunner(
                agent=agent_obj,
                execution_id=execution_id
            )
            
            # Run agent, with memory disabled if requested
            with console.status("[bold green]Agent thinking...[/bold green]"):
                if disable_memory:
                    # Run in simple mode without tools 
                    response = loop.run_until_complete(runner._run_simple(input))
                else:
                    # Run normal mode with memory
                    response = loop.run_until_complete(runner.run(input))
                loop.close()
            
            # Print response
            console.print(response)
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    else:
        console.print("[bold yellow]No input provided.[/bold yellow] Use --input or --interactive.")