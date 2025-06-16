"""
Ergon CLI - System Commands

Contains initialization, UI, status, login, and other system-level commands.
"""

import typer
from rich.console import Console
from rich.table import Table
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from ergon.utils.config.settings import settings
from ergon.core.database.engine import init_db
from ergon.cli.utils.db_helpers import ensure_db_initialized

# Initialize console for rich output
console = Console()

def init_command(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force initialization (overwrite existing setup)"
    ),
):
    """Initialize Ergon database and configuration."""
    try:
        # Check if database already exists
        if os.path.exists(settings.database_url.replace("sqlite:///", "")) and not force:
            console.print("[yellow]Database already exists. Use --force to reinitialize.[/yellow]")
            raise typer.Exit(1)
        
        with console.status("[bold green]Initializing Ergon..."):
            # Initialize database
            init_db()
            
            console.print("[bold green]✓[/bold green] Database initialized")
            
            # Create credential manager directory if it doesn't exist
            os.makedirs(settings.config_path, exist_ok=True)
            console.print(f"[bold green]✓[/bold green] Config directory created at {settings.config_path}")
            
            # Check API keys
            if settings.has_openai:
                console.print("[bold green]✓[/bold green] OpenAI API key detected")
            if settings.has_anthropic:
                console.print("[bold green]✓[/bold green] Anthropic API key detected")
            if settings.has_ollama:
                console.print("[bold green]✓[/bold green] Ollama instance detected")
                
            if not (settings.has_openai or settings.has_anthropic or settings.has_ollama):
                console.print("[yellow]⚠ No LLM API keys or local models detected.[/yellow]")
                console.print("  Set at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or ensure Ollama is running.")
        
        console.print("[bold green]Ergon initialized successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error during initialization: {str(e)}[/bold red]")
        raise typer.Exit(1)


def ui_command(
    port: int = typer.Option(8501, "--port", "-p", help="Port for the Streamlit UI"),
    host: str = typer.Option("localhost", "--host", "-h", help="Host for the Streamlit UI"),
):
    """Start the Ergon web UI (Streamlit)."""
    try:
        import streamlit.web.cli as stcli
        
        # Initialize database if not exists
        if not os.path.exists(settings.database_url.replace("sqlite:///", "")):
            console.print("[yellow]Database not initialized. Running initialization...[/yellow]")
            init_db()
        
        # Make sure config directory exists
        os.makedirs(settings.config_path, exist_ok=True)
        
        console.print(f"[bold green]Starting Ergon UI on http://{host}:{port} ...[/bold green]")
        console.print("[green]Login with your email and password. First-time users will be automatically registered.[/green]")
        
        # Run Streamlit app
        ui_path = str(Path(__file__).parent.parent.parent / "ui" / "app.py")
        console.print(f"Starting Streamlit with path: {ui_path}")
        sys.argv = ["streamlit", "run", ui_path, "--server.port", str(port), "--server.address", host]
        stcli.main()
        
    except ImportError:
        console.print("[bold red]Streamlit is not installed. Please install it with 'pip install streamlit'.[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error starting UI: {str(e)}[/bold red]")
        raise typer.Exit(1)


def status_command():
    """Check Ergon status and configuration."""
    try:
        from ergon.core.database.engine import get_db_session
        from ergon.core.database.models import Agent, DocumentationPage
        
        # Initialize database if not exists
        db_initialized = os.path.exists(settings.database_url.replace("sqlite:///", ""))
        
        table = Table(title="Ergon Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="blue")
        
        # Database status
        if db_initialized:
            table.add_row("Database", "✓", settings.database_url)
        else:
            table.add_row("Database", "✗", f"{settings.database_url} (not initialized)")
        
        # User authentication
        try:
            from ergon.utils.config.credentials import credential_manager
            cred_file_exists = os.path.exists(credential_manager.credentials_file)
            
            if cred_file_exists:
                if credential_manager.is_authenticated():
                    table.add_row("User Auth", "✓", f"Logged in as {credential_manager.get_current_user()}")
                else:
                    table.add_row("User Auth", "✓", "User account(s) exist, not logged in")
            else:
                table.add_row("User Auth", "✗", "No user accounts configured")
        except ImportError:
            table.add_row("User Auth", "✗", "Credential manager not available")
        except Exception as auth_e:
            table.add_row("User Auth", "✗", f"Error: {str(auth_e)}")
        
        # API Keys
        if settings.has_openai:
            table.add_row("OpenAI API", "✓", "API key configured")
        else:
            table.add_row("OpenAI API", "✗", "API key not configured")
            
        if settings.has_anthropic:
            table.add_row("Anthropic API", "✓", "API key configured")
        else:
            table.add_row("Anthropic API", "✗", "API key not configured")
            
        if settings.has_ollama:
            table.add_row("Ollama", "✓", settings.ollama_base_url)
        else:
            table.add_row("Ollama", "✗", f"{settings.ollama_base_url} (not available)")
            
        if settings.has_github:
            table.add_row("GitHub API", "✓", "API token configured")
        else:
            table.add_row("GitHub API", "✗", "API token not configured")
        
        # Vector store
        vector_db_exists = os.path.exists(os.path.join(settings.vector_db_path, "faiss.index"))
        if vector_db_exists:
            table.add_row("Vector Store", "✓", settings.vector_db_path)
        else:
            table.add_row("Vector Store", "✗", f"{settings.vector_db_path} (not initialized)")
        
        # Agent count
        if db_initialized:
            with get_db_session() as db:
                agent_count = db.query(Agent).count()
                doc_count = db.query(DocumentationPage).count()
                
                table.add_row("Agents", "✓" if agent_count > 0 else "✗", f"{agent_count} agent(s) available")
                table.add_row("Documentation", "✓" if doc_count > 0 else "✗", f"{doc_count} page(s) available")
                
                # Check for new repository features
                try:
                    from ergon.core.repository.models import Component
                    component_count = db.query(Component).count()
                    table.add_row("Repository", "✓" if component_count > 0 else "✓", f"{component_count} component(s) available")
                except:
                    table.add_row("Repository", "✗", "Repository tables not initialized")
                
                # Check for vector database
                try:
                    from ergon.core.docs.document_store import document_store
                    vector_count = document_store.vector_store.count_documents()
                    
                    # Check hardware detection and vector store type
                    from tekton.core.vector_store import detect_hardware, HardwareType
                    hardware = detect_hardware()
                    hardware_name = {
                        HardwareType.APPLE_SILICON: "Apple Silicon",
                        HardwareType.NVIDIA: "NVIDIA GPU",
                        HardwareType.OTHER: "Generic CPU"
                    }.get(hardware, "Unknown")
                    
                    vector_store_type = type(document_store.vector_store).__name__
                    table.add_row("Vector Store", "✓", f"{vector_count} vector(s) - {vector_store_type} on {hardware_name}")
                except Exception as vs_error:
                    table.add_row("Vector Store", "✗", f"Error: {str(vs_error)}")
                
                # Check for migrations
                try:
                    from ergon.core.database.migrations import migration_manager
                    current_revision = migration_manager.get_current_revision()
                    if current_revision and current_revision != "None" and current_revision != "Unknown":
                        table.add_row("Migrations", "✓", f"Current revision: {current_revision}")
                    else:
                        table.add_row("Migrations", "✗", "Migrations not initialized")
                except:
                    table.add_row("Migrations", "✗", "Migrations system not available")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error checking status: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        raise typer.Exit(1)


def login_command(
    email: str = typer.Option(None, "--email", "-e", help="Email address for login"),
    password: str = typer.Option(None, "--password", "-p", help="Password for login (not recommended, use prompt instead)")
):
    """Login to Ergon CLI."""
    try:
        from ergon.utils.config.credentials import credential_manager
        from ergon.utils.config.settings import settings
        
        # Check if authentication is required
        if not settings.require_authentication:
            console.print("[yellow]Authentication is disabled via ERGON_AUTHENTICATION=false.[/yellow]")
            console.print("[green]You are automatically logged in as admin@example.com[/green]")
            return
            
        # Get email if not provided
        if not email:
            email = input("Email: ").strip()
        
        # Get password if not provided (more secure)
        if not password:
            import getpass
            password = getpass.getpass("Password: ")
        
        if not email or not password:
            console.print("[bold red]Email and password are required.[/bold red]")
            return
        
        if credential_manager.authenticate(email, password):
            console.print(f"[bold green]Successfully logged in as {email}![/bold green]")
        else:
            # Check if credentials file exists
            if os.path.exists(credential_manager.credentials_file):
                console.print("[bold red]Invalid credentials.[/bold red]")
                
                # Ask if they want to register
                if typer.confirm("Would you like to register as a new user?"):
                    register_new_user(email)
            else:
                # First time setup
                console.print("[yellow]No users registered yet. Creating new account.[/yellow]")
                register_new_user(email)
                
    except ImportError:
        console.print("[bold red]Credential manager not available. Initialize Ergon first.[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error during login: {str(e)}[/bold red]")
        raise typer.Exit(1)


def register_new_user(email=None):
    """Helper function to register a new user."""
    from ergon.utils.config.credentials import credential_manager
    import getpass
    
    if not email:
        email = input("Email: ").strip()
    
    while True:
        password = getpass.getpass("Password (minimum 8 characters): ")
        
        if not password:
            console.print("[bold red]Password cannot be empty.[/bold red]")
            continue
            
        if len(password) < 8:
            console.print("[bold red]Password must be at least 8 characters.[/bold red]")
            continue
            
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            console.print("[bold red]Passwords do not match.[/bold red]")
            continue
        
        break
        
    if credential_manager.register(email, password):
        console.print(f"[bold green]Successfully registered and logged in as {email}![/bold green]")
        return True
    else:
        console.print("[bold red]Registration failed. User may already exist.[/bold red]")
        return False


def setup_mail_command(
    provider: str = typer.Option("interactive", help="Mail provider type (gmail, outlook, imap, or interactive)"),
    interactive: bool = typer.Option(True, help="Use interactive setup"),
    # IMAP parameters
    email: str = typer.Option(None, help="Email address (for IMAP provider)"),
    password: str = typer.Option(None, help="Password (for IMAP provider, not recommended via command line)"),
    imap_server: str = typer.Option(None, help="IMAP server (for IMAP provider)"),
    smtp_server: str = typer.Option(None, help="SMTP server (for IMAP provider)"),
    imap_port: int = typer.Option(993, help="IMAP port (for IMAP provider)"),
    smtp_port: int = typer.Option(587, help="SMTP port (for IMAP provider)"),
    use_ssl: bool = typer.Option(True, help="Use SSL for IMAP (for IMAP provider)"),
    use_tls: bool = typer.Option(True, help="Use TLS for SMTP (for IMAP provider)"),
    # OAuth parameters
    credentials_file: str = typer.Option(None, help="Path to OAuth credentials file (for Gmail/Outlook)")
):
    """Set up mail provider for Ergon.
    
    For non-interactive IMAP setup, provide email, password, and server information.
    For Gmail, provide credentials_file or place credentials at ~/.ergon/gmail_credentials.json
    For Outlook, set OUTLOOK_CLIENT_ID in your .env file.
    """
    try:
        from ergon.core.agents.mail.setup import setup_mail_provider
        
        if provider.lower() == "interactive":
            provider_arg = None
        else:
            if provider.lower() not in ["gmail", "outlook", "imap"]:
                console.print(f"[bold red]Invalid provider: {provider}[/bold red]")
                console.print("Valid providers: gmail, outlook, imap")
                raise typer.Exit(1)
            provider_arg = provider.lower()
        
        # For non-interactive IMAP setup, check required params
        if not interactive and provider_arg == "imap" and (not email or not password):
            console.print("[bold red]Email and password are required for non-interactive IMAP setup[/bold red]")
            raise typer.Exit(1)
            
        # Warn about password on command line
        if password:
            console.print("[bold red]WARNING: SECURITY RISK[/bold red]")
            console.print("[bold yellow]Providing passwords on the command line is not secure:[/bold yellow]")
            console.print("[yellow]- Password may be visible in your shell history or process list[/yellow]")
            console.print("[yellow]- Password will be stored in plain text in the configuration file[/yellow]")
            console.print("[yellow]- In production, use environment variables or a secure credential store[/yellow]")
            
            if not typer.confirm("Do you want to continue with this insecure method?"):
                console.print("[green]Aborted. Consider using the interactive setup instead.[/green]")
                raise typer.Exit(0)
            
        # Run setup
        with console.status(f"[bold green]Setting up {provider} mail provider..."):
            result = asyncio.run(setup_mail_provider(
                provider_type=provider_arg,
                interactive=interactive,
                email_address=email,
                password=password,
                imap_server=imap_server,
                smtp_server=smtp_server,
                imap_port=imap_port,
                smtp_port=smtp_port,
                use_ssl=use_ssl,
                use_tls=use_tls,
                credentials_file=credentials_file
            ))
        
        if result:
            console.print(f"[bold green]✓ Mail setup completed successfully![/bold green]")
        else:
            console.print(f"[bold red]✗ Mail setup failed.[/bold red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Error setting up mail: {str(e)}[/bold red]")
        raise typer.Exit(1)