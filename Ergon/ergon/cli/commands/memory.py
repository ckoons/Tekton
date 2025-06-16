"""
Command-line interface for memory management.

This module provides commands for managing memory in Ergon agents.
"""

import os
import asyncio
import typer
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from datetime import datetime

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent
from ergon.core.memory.models.schema import Memory
from ergon.core.memory.service import MemoryService
from ergon.core.memory.utils.categories import MemoryCategory
from ergon.core.memory.services.client import client_manager
from ergon.utils.config.settings import settings

# Initialize Typer app
memory_app = typer.Typer(help="Memory management commands")
console = Console()

def _get_agent_by_id_or_name(agent_id_or_name: str) -> Optional[Agent]:
    """
    Get agent by ID or name.
    
    Args:
        agent_id_or_name: Agent ID or name
        
    Returns:
        Agent instance or None if not found
    """
    with get_db_session() as db:
        # Try as ID first
        try:
            agent_id = int(agent_id_or_name)
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                return agent
        except ValueError:
            pass
        
        # Try as name
        agent = db.query(Agent).filter(Agent.name == agent_id_or_name).first()
        return agent

def _print_memory_table(memories: List[dict], title: str = "Memories"):
    """Print a formatted table of memories."""
    table = Table(title=title)
    table.add_column("ID", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Importance", justify="center")
    table.add_column("Created", style="green")
    table.add_column("Content")

    for memory in memories:
        # Format importance as stars
        importance_str = "★" * memory["importance"]
        # Format date
        date_str = memory["created_at"].strftime("%Y-%m-%d %H:%M")
        # Format content (truncate if too long)
        content = memory["content"]
        if len(content) > 80:
            content = content[:77] + "..."
            
        table.add_row(
            memory["id"][-8:],  # Show just the end of the ID
            memory["category"].capitalize(),
            importance_str,
            date_str,
            content
        )
        
    console.print(table)

@memory_app.command("list")
def list_memories(
    agent: str = typer.Argument(..., help="Agent ID or name"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    min_importance: int = typer.Option(1, "--min-importance", "-i", help="Minimum importance"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of memories to show"),
    all_categories: bool = typer.Option(False, "--all-categories", help="List all available categories")
):
    """List memories for an agent."""
    # Get agent
    agent_obj = _get_agent_by_id_or_name(agent)
    if not agent_obj:
        typer.echo(f"Agent not found: {agent}")
        raise typer.Exit(code=1)
    
    # Set up memory service
    memory_service = MemoryService(agent_id=agent_obj.id, agent_name=agent_obj.name)
    
    async def _list_memories():
        if all_categories:
            # Get memories for each category
            categories = list(MemoryCategory.ALL_CATEGORIES)
            
            total_shown = 0
            for cat in categories:
                memories = await memory_service.get_by_category(
                    category=cat,
                    limit=3  # Just show a few per category
                )
                
                if memories:
                    _print_memory_table(
                        memories, 
                        title=f"Category: {cat.capitalize()} (showing 3 of {len(memories)})"
                    )
                    total_shown += len(memories)
            
            if total_shown == 0:
                typer.echo("No memories found.")
        else:
            # Get memories with filters
            categories = [category] if category else None
            memories = await memory_service.get_recent(
                categories=categories,
                min_importance=min_importance,
                limit=limit
            )
            
            if not memories:
                typer.echo("No memories found for the given criteria.")
                return
                
            _print_memory_table(
                memories,
                title=f"Memories for {agent_obj.name} (ID: {agent_obj.id})"
            )
    
    # Run the async function
    asyncio.run(_list_memories())
    
@memory_app.command("search")
def search_memories(
    agent: str = typer.Argument(..., help="Agent ID or name"),
    query: str = typer.Argument(..., help="Search query"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    min_importance: int = typer.Option(1, "--min-importance", "-i", help="Minimum importance"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results")
):
    """Search agent memories by query."""
    # Get agent
    agent_obj = _get_agent_by_id_or_name(agent)
    if not agent_obj:
        typer.echo(f"Agent not found: {agent}")
        raise typer.Exit(code=1)
    
    # Set up memory service
    memory_service = MemoryService(agent_id=agent_obj.id, agent_name=agent_obj.name)
    
    async def _search_memories():
        # Search memories
        categories = [category] if category else None
        memories = await memory_service.search(
            query=query,
            categories=categories,
            min_importance=min_importance,
            limit=limit
        )
        
        if not memories:
            typer.echo("No memories found matching the query.")
            return
            
        _print_memory_table(
            memories, 
            title=f"Search results for '{query}'"
        )
    
    # Run the async function
    asyncio.run(_search_memories())

@memory_app.command("add")
def add_memory(
    agent: str = typer.Argument(..., help="Agent ID or name"),
    content: str = typer.Argument(..., help="Memory content"),
    category: str = typer.Option(MemoryCategory.FACTUAL, "--category", "-c", help="Memory category"),
    importance: int = typer.Option(3, "--importance", "-i", help="Importance (1-5)")
):
    """Add a new memory for an agent."""
    # Validate category
    if not MemoryCategory.is_valid_category(category):
        valid_categories = ", ".join(sorted(MemoryCategory.ALL_CATEGORIES))
        typer.echo(f"Invalid category: {category}")
        typer.echo(f"Valid categories: {valid_categories}")
        raise typer.Exit(code=1)
    
    # Validate importance
    importance = max(1, min(5, importance))
    
    # Get agent
    agent_obj = _get_agent_by_id_or_name(agent)
    if not agent_obj:
        typer.echo(f"Agent not found: {agent}")
        raise typer.Exit(code=1)
    
    # Set up memory service
    memory_service = MemoryService(agent_id=agent_obj.id, agent_name=agent_obj.name)
    
    async def _add_memory():
        # Add memory
        memory_id = await memory_service.add_memory(
            content=content,
            category=category,
            importance=importance
        )
        
        typer.echo(f"Memory added with ID: {memory_id}")
        
        # Show the added memory
        memories = await memory_service.search(query=content, limit=1)
        if memories:
            _print_memory_table(memories, title="Added Memory")
    
    # Run the async function
    asyncio.run(_add_memory())

@memory_app.command("delete")
def delete_memory(
    agent: str = typer.Argument(..., help="Agent ID or name"),
    memory_id: str = typer.Argument(..., help="Memory ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Delete a memory by ID."""
    # Get agent
    agent_obj = _get_agent_by_id_or_name(agent)
    if not agent_obj:
        typer.echo(f"Agent not found: {agent}")
        raise typer.Exit(code=1)
    
    # Set up memory service
    memory_service = MemoryService(agent_id=agent_obj.id, agent_name=agent_obj.name)
    
    async def _delete_memory():
        # Confirm deletion
        if not force:
            with get_db_session() as db:
                memory = db.query(Memory).filter(Memory.id == memory_id).first()
                
                if not memory:
                    typer.echo(f"Memory not found: {memory_id}")
                    return
                    
                typer.echo(f"Memory ID: {memory_id}")
                typer.echo(f"Category: {memory.category}")
                typer.echo(f"Importance: {memory.importance}")
                typer.echo(f"Content: {memory.content}")
                
                confirm = typer.confirm("Are you sure you want to delete this memory?")
                if not confirm:
                    typer.echo("Deletion cancelled.")
                    return
        
        # Delete memory
        success = await memory_service.delete_memory(memory_id)
        
        if success:
            typer.echo(f"Memory {memory_id} deleted successfully.")
        else:
            typer.echo(f"Failed to delete memory {memory_id}.")
    
    # Run the async function
    asyncio.run(_delete_memory())

@memory_app.command("clear")
def clear_memories(
    agent: str = typer.Argument(..., help="Agent ID or name"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Category to clear (if not specified, all memories are cleared)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Clear memories for an agent."""
    # Get agent
    agent_obj = _get_agent_by_id_or_name(agent)
    if not agent_obj:
        typer.echo(f"Agent not found: {agent}")
        raise typer.Exit(code=1)
    
    # Set up memory service
    memory_service = MemoryService(agent_id=agent_obj.id, agent_name=agent_obj.name)
    
    async def _clear_memories():
        # Confirm deletion
        if not force:
            with get_db_session() as db:
                if category:
                    count = db.query(Memory).filter(
                        Memory.agent_id == agent_obj.id,
                        Memory.category == category
                    ).count()
                    typer.echo(f"This will delete {count} memories in category '{category}' for agent {agent_obj.name}.")
                else:
                    count = db.query(Memory).filter(Memory.agent_id == agent_obj.id).count()
                    typer.echo(f"This will delete ALL {count} memories for agent {agent_obj.name}.")
                
                if count == 0:
                    typer.echo("No memories to delete.")
                    return
                
                confirm = typer.confirm("Are you sure you want to proceed?")
                if not confirm:
                    typer.echo("Operation cancelled.")
                    return
        
        # Clear memories
        if category:
            deleted = await memory_service.clear_category(category)
            typer.echo(f"Cleared {deleted} memories in category '{category}'.")
        else:
            deleted = await memory_service.clear_all()
            typer.echo(f"Cleared all {deleted} memories for agent {agent_obj.name}.")
    
    # Run the async function
    asyncio.run(_clear_memories())

@memory_app.command("categories")
def list_categories():
    """List all available memory categories."""
    table = Table(title="Memory Categories")
    table.add_column("Category", style="cyan")
    table.add_column("Default Importance", justify="center")
    table.add_column("Description")
    
    categories = {
        MemoryCategory.PERSONAL: "Personal details about the user",
        MemoryCategory.FACTUAL: "Factual information learned",
        MemoryCategory.SESSION: "Current session details",
        MemoryCategory.PROJECT: "Project-specific information",
        MemoryCategory.PREFERENCE: "User preferences",
        MemoryCategory.SYSTEM: "System-related memories"
    }
    
    for category, description in categories.items():
        importance = MemoryCategory.get_default_importance(category)
        importance_str = "★" * importance
        
        table.add_row(
            category.capitalize(),
            importance_str,
            description
        )
    
    console.print(table)

# Client management commands
@memory_app.command("clients")
def list_clients():
    """List all registered memory clients."""
    async def _list_clients():
        # Start client manager if not running
        await client_manager.start()
        
        # Get all clients
        with client_manager.lock:
            clients = client_manager.active_clients
            
        if not clients:
            typer.echo("No active memory clients registered.")
            return
            
        # Create table
        table = Table(title="Memory Clients")
        table.add_column("Client ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Registered At", style="green")
        table.add_column("Last Active", style="green")
        
        for client_id, info in clients.items():
            registered_at = info["registered_at"].strftime("%Y-%m-%d %H:%M:%S")
            last_active = info["last_active"].strftime("%Y-%m-%d %H:%M:%S")
            
            table.add_row(
                client_id,
                info["type"],
                registered_at,
                last_active
            )
            
        console.print(table)
    
    # Run the async function
    asyncio.run(_list_clients())

@memory_app.command("register")
def register_client(
    client_id: str = typer.Argument(..., help="Unique client ID"),
    client_type: str = typer.Argument(..., help="Client type (ollama, openai, anthropic)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name for the client"),
    config_json: Optional[str] = typer.Option(None, "--config", "-c", help="JSON string with additional configuration")
):
    """Register a new memory client."""
    import json
    
    # Parse config if provided
    config = {}
    if config_json:
        try:
            config = json.loads(config_json)
        except json.JSONDecodeError:
            typer.echo(f"Invalid JSON configuration: {config_json}")
            raise typer.Exit(code=1)
    
    # Add model to config if provided
    if model:
        config["model"] = model
    
    async def _register_client():
        # Start client manager if not running
        await client_manager.start()
        
        # Register client
        success = await client_manager.register_client(
            client_id=client_id,
            client_type=client_type,
            config=config
        )
        
        if success:
            typer.echo(f"Client '{client_id}' registered successfully.")
            
            # Get client info
            info = await client_manager.get_client_info(client_id)
            if info:
                typer.echo(f"Type: {info['type']}")
                typer.echo(f"Registered at: {info['registered_at']}")
                
                # Print config (excluding sensitive values)
                safe_config = {k: v for k, v in info['config'].items() if k not in ('api_key', 'password', 'token')}
                if safe_config:
                    typer.echo(f"Configuration: {json.dumps(safe_config)}")
        else:
            typer.echo(f"Failed to register client '{client_id}'.")
    
    # Run the async function
    asyncio.run(_register_client())

@memory_app.command("deregister")
def deregister_client(
    client_id: str = typer.Argument(..., help="Client ID to deregister"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deregistration without confirmation")
):
    """Deregister a memory client."""
    async def _deregister_client():
        # Start client manager if not running
        await client_manager.start()
        
        # Get client info for confirmation
        info = await client_manager.get_client_info(client_id)
        if not info:
            typer.echo(f"Client not found: {client_id}")
            return
        
        # Confirm deregistration
        if not force:
            typer.echo(f"Client ID: {client_id}")
            typer.echo(f"Type: {info['type']}")
            typer.echo(f"Registered at: {info['registered_at']}")
            typer.echo(f"Last active: {info['last_active']}")
            
            confirm = typer.confirm("Are you sure you want to deregister this client?")
            if not confirm:
                typer.echo("Deregistration cancelled.")
                return
        
        # Deregister client
        success = await client_manager.deregister_client(client_id)
        
        if success:
            typer.echo(f"Client '{client_id}' deregistered successfully.")
        else:
            typer.echo(f"Failed to deregister client '{client_id}'.")
    
    # Run the async function
    asyncio.run(_deregister_client())

@memory_app.command("client-info")
def client_info(
    client_id: str = typer.Argument(..., help="Client ID to get info for")
):
    """Get detailed information about a memory client."""
    async def _get_client_info():
        # Start client manager if not running
        await client_manager.start()
        
        # Get client info
        info = await client_manager.get_client_info(client_id)
        if not info:
            typer.echo(f"Client not found: {client_id}")
            return
        
        # Print client info
        typer.echo(f"Client ID: {client_id}")
        typer.echo(f"Type: {info['type']}")
        typer.echo(f"Registered at: {info['registered_at']}")
        typer.echo(f"Last active: {info['last_active']}")
        
        # Print config (excluding sensitive values)
        safe_config = {k: v for k, v in info['config'].items() if k not in ('api_key', 'password', 'token')}
        if safe_config:
            typer.echo(f"Configuration: {json.dumps(safe_config, indent=2)}")
        
        # Print metadata
        if info['metadata']:
            typer.echo(f"Metadata: {json.dumps(info['metadata'], indent=2)}")
    
    # Run the async function
    asyncio.run(_get_client_info())