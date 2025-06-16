"""
Ergon CLI - Database Helpers

Utility functions for database operations.
"""

import os
from rich.console import Console
import typer

from ergon.utils.config.settings import settings
from ergon.core.database.engine import init_db

# Initialize console for rich output
console = Console()

def ensure_db_initialized():
    """
    Ensure database is initialized.
    
    Checks if database exists and initializes it if not.
    
    Returns:
        bool: True if database was already initialized, False if it was just initialized
    """
    # Initialize database if not exists
    if not os.path.exists(settings.database_url.replace("sqlite:///", "")):
        console.print("[yellow]Database not initialized. Running initialization...[/yellow]")
        init_db()
        return False
    return True


def check_database_tables(required_tables=None):
    """
    Check if specific database tables exist.
    
    Args:
        required_tables: List of table names to check for
        
    Returns:
        bool: True if all required tables exist, False otherwise
    """
    from sqlalchemy import inspect
    from ergon.core.database.engine import get_engine
    
    required_tables = required_tables or []
    
    if not ensure_db_initialized():
        return False
    
    # Check for specific tables
    if required_tables:
        engine = get_engine()
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        for table in required_tables:
            if table not in existing_tables:
                console.print(f"[yellow]Required table '{table}' not found in database.[/yellow]")
                return False
    
    return True