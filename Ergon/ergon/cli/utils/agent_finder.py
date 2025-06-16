"""
Ergon CLI - Agent Finder Utility

Helpers for finding agents by name or ID.
"""

from typing import Optional
from sqlalchemy.orm import Session
from rich.console import Console
import typer

from ergon.core.database.models import Agent as DatabaseAgent

# Initialize console for rich output
console = Console()

def find_agent_by_identifier(db: Session, agent_identifier: str) -> Optional[DatabaseAgent]:
    """
    Find an agent by ID or name.
    
    Args:
        db: Database session
        agent_identifier: Agent ID or name
        
    Returns:
        DatabaseAgent or None if not found
    """
    identifier_type = "name"
    
    # Check if identifier is an integer (likely an ID)
    try:
        agent_id = int(agent_identifier)
        agent = db.query(DatabaseAgent).filter(DatabaseAgent.id == agent_id).first()
        if agent:
            identifier_type = "ID"
            return agent
        # Fall through to name search if ID not found
    except ValueError:
        # Not an integer, so continue with name search
        pass
    
    # Search by exact name match
    agent = db.query(DatabaseAgent).filter(DatabaseAgent.name == agent_identifier).first()
    if agent:
        return agent
    
    # Try a case-insensitive partial match on name
    agent = db.query(DatabaseAgent).filter(DatabaseAgent.name.ilike(f"%{agent_identifier}%")).first()
    
    if agent:
        console.print(f"[yellow]Agent with exact {identifier_type} '{agent_identifier}' not found, but found matching agent '{agent.name}'.[/yellow]")
        return agent
    
    # Not found, provide helpful suggestions
    console.print(f"[bold red]Agent with {identifier_type} '{agent_identifier}' not found.[/bold red]")
    
    # List available agents
    agents = db.query(DatabaseAgent).all()
    if agents:
        console.print("[yellow]Available agents:[/yellow]")
        for a in agents:
            console.print(f"  {a.id}: {a.name}")
    
    return None