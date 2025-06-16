"""
Documentation system commands for the Ergon CLI.
"""

import os
import asyncio
import logging
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from ergon.core.docs.document_store import document_store
from ergon.core.docs.crawler import (
    crawl_all_docs, 
    crawl_pydantic_ai_docs, 
    crawl_langchain_docs, 
    crawl_anthropic_docs, 
    crawl_langgraph_docs
)

# Create typer app
app = typer.Typer(help="Documentation system commands")

# Create console
console = Console()

# Configure logger
logger = logging.getLogger(__name__)


@app.command("search")
def search_docs(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results to return"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, text)")
):
    """
    Search documentation.
    """
    # Execute search
    results = asyncio.run(document_store.search_documentation(query, limit=limit))
    
    if not results:
        console.print(Panel("No matching documentation found.", title="Search Results", border_style="yellow"))
        return
    
    if format == "table":
        # Create results table
        table = Table(title=f"Search Results for: {query}")
        table.add_column("Score", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Content", style="white")
        table.add_column("Source", style="blue")
        
        for result in results:
            score = f"{result.get('score', 0):.2f}"
            title = result.get("metadata", {}).get("title", "Untitled")
            content = result["content"][:100] + "..." if len(result["content"]) > 100 else result["content"]
            source = result.get("metadata", {}).get("source", "Unknown")
            
            table.add_row(score, title, content, source)
        
        console.print(table)
    else:
        # Plain text output
        console.print(f"Search Results for: {query}")
        console.print("=" * 80)
        
        for i, result in enumerate(results):
            score = f"{result.get('score', 0):.2f}"
            title = result.get("metadata", {}).get("title", "Untitled")
            content = result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
            source = result.get("metadata", {}).get("source", "Unknown")
            
            console.print(f"[{i+1}] {title} (Score: {score}, Source: {source})")
            console.print(f"{content}")
            console.print("-" * 80)


@app.command("add")
def add_documentation(
    title: str = typer.Option(..., "--title", "-t", help="Documentation title"),
    content: str = typer.Option(None, "--content", "-c", help="Documentation content"),
    content_file: str = typer.Option(None, "--file", "-f", help="File containing documentation content"),
    url: str = typer.Option("", "--url", "-u", help="Documentation URL"),
    source: str = typer.Option("manual", "--source", "-s", help="Documentation source")
):
    """
    Add documentation manually.
    """
    # Validate input
    if content is None and content_file is None:
        console.print("[bold red]Error:[/bold red] Either content or content_file must be provided.")
        return
    
    # Read content from file if provided
    if content_file:
        if not os.path.exists(content_file):
            console.print(f"[bold red]Error:[/bold red] File not found: {content_file}")
            return
        
        with open(content_file, "r") as f:
            content = f.read()
    
    # Add documentation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Adding documentation...", total=1)
        
        # Add documentation
        doc_id = asyncio.run(document_store.add_documentation(
            title=title,
            content=content,
            url=url,
            source=source
        ))
        
        progress.update(task, advance=1)
    
    console.print(f"[green]Documentation added successfully.[/green] ID: {doc_id}")


@app.command("crawl")
def crawl_documentation(
    source: str = typer.Option("all", "--source", "-s", 
                               help="Documentation source to crawl (all, pydantic, langchain, anthropic, langgraph)"),
    max_pages: int = typer.Option(100, "--max-pages", "-m", help="Maximum number of pages to crawl"),
    max_depth: int = typer.Option(3, "--max-depth", "-d", help="Maximum crawl depth")
):
    """
    Crawl documentation from external sources.
    """
    # Validate source
    valid_sources = ["all", "pydantic", "langchain", "anthropic", "langgraph"]
    if source not in valid_sources:
        console.print(f"[bold red]Error:[/bold red] Invalid source. Valid options: {', '.join(valid_sources)}")
        return
    
    # Set up progress tracking
    pages_crawled = 0
    
    def progress_callback():
        nonlocal pages_crawled
        pages_crawled += 1
    
    # Start crawling
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total} pages)"),
    ) as progress:
        task = progress.add_task(f"Crawling {source} documentation...", total=max_pages)
        
        # Run appropriate crawler
        if source == "all":
            result = asyncio.run(crawl_all_docs(
                max_pages=max_pages,
                max_depth=max_depth,
                progress_callback=lambda: progress.update(task, advance=1)
            ))
        elif source == "pydantic":
            result = asyncio.run(crawl_pydantic_ai_docs(
                max_pages=max_pages,
                max_depth=max_depth,
                progress_callback=lambda: progress.update(task, advance=1)
            ))
        elif source == "langchain":
            result = asyncio.run(crawl_langchain_docs(
                max_pages=max_pages,
                max_depth=max_depth,
                progress_callback=lambda: progress.update(task, advance=1)
            ))
        elif source == "anthropic":
            result = asyncio.run(crawl_anthropic_docs(
                max_pages=max_pages,
                max_depth=max_depth,
                progress_callback=lambda: progress.update(task, advance=1)
            ))
        elif source == "langgraph":
            result = asyncio.run(crawl_langgraph_docs(
                max_pages=max_pages,
                max_depth=max_depth,
                progress_callback=lambda: progress.update(task, advance=1)
            ))
        
        # Update progress to completion
        progress.update(task, completed=progress.tasks[0].completed)
    
    console.print(f"[green]Crawling completed.[/green] Pages indexed: {result}")


@app.command("index-components")
def index_components():
    """
    Index components in the repository.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Indexing components...", total=1)
        
        # Index components
        count = asyncio.run(document_store.index_components())
        
        progress.update(task, advance=1)
    
    console.print(f"[green]Component indexing completed.[/green] Components indexed: {count}")


if __name__ == "__main__":
    app()