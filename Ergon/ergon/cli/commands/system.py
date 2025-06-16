"""
CLI commands for system information and management.
"""

import typer
from typing import Optional, List
import json
from rich.console import Console
from rich.table import Table

from ergon.utils.config.settings import settings
from tekton.core.vector_store import detect_hardware, HardwareType

app = typer.Typer(help="System information and management")
console = Console()


@app.command("info")
def system_info():
    """Display information about the system configuration."""
    console.print("[cyan]Ergon System Information[/cyan]")
    console.print(f"[green]Vector Database Path:[/green] {settings.vector_db_path}")
    console.print(f"[green]Data Directory:[/green] {settings.data_dir}")
    
    # Hardware detection
    hardware = detect_hardware()
    hardware_name = {
        HardwareType.APPLE_SILICON: "Apple Silicon",
        HardwareType.NVIDIA: "NVIDIA GPU",
        HardwareType.OTHER: "Generic CPU"
    }.get(hardware, "Unknown")
    
    console.print(f"[green]Detected Hardware:[/green] {hardware_name}")
    
    # Vector store implementation
    from ergon.core.docs.document_store import document_store
    vector_store_type = type(document_store.vector_store).__name__
    
    console.print(f"[green]Vector Store Implementation:[/green] {vector_store_type}")
    console.print(f"[green]Embedding Model:[/green] {settings.embedding_model}")
    
    # Available models
    console.print("[green]Available LLM Models:[/green]")
    for model in settings.available_models:
        console.print(f"  - {model}")


@app.command("check-vector-store")
def check_vector_store():
    """Check vector store information and document count."""
    from ergon.core.docs.document_store import document_store
    
    console.print("[cyan]Vector Store Information[/cyan]")
    console.print(f"[green]Implementation:[/green] {type(document_store.vector_store).__name__}")
    console.print(f"[green]Path:[/green] {document_store.vector_db_path}")
    
    # Get document count
    doc_count = document_store.vector_store.count_documents()
    console.print(f"[green]Total Documents:[/green] {doc_count}")
    
    # Check if we can search
    try:
        results = document_store.vector_store.search("test", top_k=1)
        console.print(f"[green]Search Operational:[/green] Yes")
    except Exception as e:
        console.print(f"[red]Search Operational:[/red] No - Error: {str(e)}")