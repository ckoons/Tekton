"""
Ergon Command Line Interface - Core Module

Contains the core Typer application and configuration.
"""

import typer
from rich.console import Console
from typing import Optional, List
import os
import sys
from pathlib import Path

# Import settings
from ergon.utils.config.settings import settings

# Initialize console for rich output
console = Console()

# Create Typer app
app = typer.Typer(
    name="ergon",
    help="Ergon: Intelligent Tool, Agent, and Workflow Manager",
    add_completion=False,
)

def version_callback(value: bool):
    """Display version information."""
    if value:
        from ergon import __version__
        console.print(f"Ergon CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, help="Show version information."
    ),
):
    """Ergon CLI: Intelligent Tool, Agent, and Workflow Manager."""
    # Check if authenticated
    try:
        from ergon.utils.config.credentials import credential_manager
    except ImportError:
        # Credential manager not available yet
        pass


def load_commands():
    """Load all command modules and add them to the CLI app."""
    # Import commands
    from ergon.cli.commands.nexus import nexus_command
    from ergon.cli.commands.repository import app as repo_app
    from ergon.cli.commands.docs import app as docs_app
    from ergon.cli.commands.tools import app as tools_app
    from ergon.cli.commands.db import app as db_app
    from ergon.cli.commands.system import app as system_app
    from ergon.cli.commands.memory import memory_app
    
    # Import agent management commands
    from ergon.cli.commands.agent_commands import (
        create_agent,
        list_agents,
        run_agent,
        delete_agent
    )
    
    # Import system commands
    from ergon.cli.commands.system_commands import (
        init_command,
        ui_command,
        status_command,
        login_command,
        setup_mail_command
    )
    
    # Import flow commands
    from ergon.cli.commands.flow_commands import run_flow_command
    
    # Import docs commands
    from ergon.cli.commands.docs_commands import preload_docs_command
    
    # Import latent reasoning commands if available
    try:
        from ergon.cli.commands.latent import app as latent_app
        HAS_LATENT_REASONING = True
    except ImportError:
        HAS_LATENT_REASONING = False
    
    # Add subcommands
    app.add_typer(repo_app, name="repo", help="Repository management commands")
    app.add_typer(docs_app, name="docs", help="Documentation system commands")
    app.add_typer(tools_app, name="tools", help="Tool generation commands")
    app.add_typer(db_app, name="db", help="Database management commands")
    app.add_typer(system_app, name="system", help="System information and management")
    app.add_typer(memory_app, name="memory", help="Memory management commands")
    
    # Add latent reasoning commands if available
    if HAS_LATENT_REASONING:
        app.add_typer(latent_app, name="latent", help="Latent reasoning commands")
    
    # Add commands
    app.command("init")(init_command)
    app.command("ui")(ui_command)
    app.command("create")(create_agent)
    app.command("list")(list_agents)
    app.command("run")(run_agent)
    app.command("delete")(delete_agent)
    app.command("nexus")(nexus_command)
    app.command("preload-docs")(preload_docs_command)
    app.command("flow")(run_flow_command)
    app.command("login")(login_command)
    app.command("status")(status_command)
    app.command("setup-mail")(setup_mail_command)