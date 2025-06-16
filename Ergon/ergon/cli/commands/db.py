"""
Database management commands for the Ergon CLI.
"""

import os
import logging
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ergon.core.database.migrations import migration_manager
from ergon.utils.config.settings import settings

# Create typer app
app = typer.Typer(help="Database management commands")

# Create console
console = Console()

# Configure logger
logger = logging.getLogger(__name__)


@app.command("init")
def init_migrations():
    """
    Initialize database migrations.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Initializing migrations...", total=1)
        
        # Initialize migrations
        success = migration_manager.init()
        
        progress.update(task, advance=1)
    
    if success:
        console.print("[green]Migrations initialized successfully.[/green]")
    else:
        console.print("[bold red]Error:[/bold red] Failed to initialize migrations.")


@app.command("create")
def create_migration(
    message: str = typer.Argument("database update", help="Migration message")
):
    """
    Create a new migration.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Creating migration...", total=1)
        
        # Create migration
        revision = migration_manager.create_migration(message)
        
        progress.update(task, advance=1)
    
    if revision:
        console.print(f"[green]Migration created successfully.[/green] Revision: {revision}")
    else:
        console.print("[bold red]Error:[/bold red] Failed to create migration.")


@app.command("upgrade")
def upgrade_database(
    revision: str = typer.Argument("head", help="Target revision (default: head)")
):
    """
    Upgrade database to revision.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Upgrading database to {revision}...", total=1)
        
        # Upgrade database
        success = migration_manager.upgrade(revision)
        
        progress.update(task, advance=1)
    
    if success:
        console.print(f"[green]Database upgraded successfully to {revision}.[/green]")
    else:
        console.print(f"[bold red]Error:[/bold red] Failed to upgrade database to {revision}.")


@app.command("downgrade")
def downgrade_database(
    revision: str = typer.Argument(..., help="Target revision")
):
    """
    Downgrade database to revision.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Downgrading database to {revision}...", total=1)
        
        # Downgrade database
        success = migration_manager.downgrade(revision)
        
        progress.update(task, advance=1)
    
    if success:
        console.print(f"[green]Database downgraded successfully to {revision}.[/green]")
    else:
        console.print(f"[bold red]Error:[/bold red] Failed to downgrade database to {revision}.")


@app.command("current")
def get_current_revision():
    """
    Get current database revision.
    """
    revision = migration_manager.get_current_revision()
    console.print(f"Current database revision: [bold]{revision}[/bold]")


@app.command("list")
def list_migrations():
    """
    List all migrations.
    """
    migrations = migration_manager.get_migrations()
    
    if not migrations:
        console.print("No migrations found.")
        return
    
    # Create results table
    table = Table(title="Database Migrations")
    table.add_column("Revision", style="cyan", no_wrap=True)
    table.add_column("Down Revision", style="green")
    table.add_column("Message", style="white")
    table.add_column("Date", style="blue")
    table.add_column("Status", style="yellow")
    
    for migration in migrations:
        revision = migration["revision"]
        down_revision = migration["down_revision"] or "None"
        message = migration["message"] or "No message"
        date = migration["date"] or "Unknown"
        status = "[bold green]CURRENT[/bold green]" if migration["is_current"] else ""
        
        table.add_row(revision, down_revision, message, date, status)
    
    console.print(table)


@app.command("backup")
def backup_database(
    output_path: str = typer.Option(None, "--output", "-o", help="Output path for backup file")
):
    """
    Backup database.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Backing up database...", total=1)
        
        # Backup database
        backup_path = migration_manager.backup_database(output_path)
        
        progress.update(task, advance=1)
    
    if backup_path:
        console.print(f"[green]Database backed up successfully.[/green] Backup saved to: {backup_path}")
    else:
        console.print("[bold red]Error:[/bold red] Failed to backup database.")


@app.command("restore")
def restore_database(
    backup_path: str = typer.Argument(..., help="Path to backup file"),
    force: bool = typer.Option(False, "--force", "-f", help="Force restore without confirmation")
):
    """
    Restore database from backup.
    """
    if not os.path.exists(backup_path):
        console.print(f"[bold red]Error:[/bold red] Backup file not found: {backup_path}")
        return
    
    # Confirm restore if not forced
    if not force:
        console.print("[yellow]Warning: This will overwrite the current database. Make sure you have a backup.[/yellow]")
        confirm = typer.confirm("Do you want to continue?")
        if not confirm:
            console.print("Restore cancelled.")
            return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Restoring database...", total=1)
        
        # Restore database
        success = migration_manager.restore_database(backup_path)
        
        progress.update(task, advance=1)
    
    if success:
        console.print(f"[green]Database restored successfully from {backup_path}.[/green]")
    else:
        console.print(f"[bold red]Error:[/bold red] Failed to restore database from {backup_path}.")


if __name__ == "__main__":
    app()