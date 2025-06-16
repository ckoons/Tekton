"""
Ergon CLI - Documentation Commands

Contains commands for managing document sources and preloading documentation.
"""

import typer
from rich.console import Console
import os
import asyncio
from typing import Optional

from ergon.utils.config.settings import settings
from ergon.core.database.engine import init_db
from ergon.cli.utils.db_helpers import ensure_db_initialized

# Initialize console for rich output
console = Console()

def preload_docs_command(
    source: str = typer.Option("all", "--source", "-s", help="Documentation source(s) to preload: all, pydantic, langchain, langgraph, anthropic"),
    max_pages: int = typer.Option(300, "--max-pages", "-m", help="Maximum number of pages to crawl"),
    max_depth: int = typer.Option(3, "--max-depth", "-d", help="Maximum link depth to crawl"),
    timeout: int = typer.Option(600, "--timeout", "-t", help="HTTP request timeout in seconds (max 600)")
):
    """Preload documentation from specified sources for agent context augmentation."""
    try:
        from ergon.core.docs.crawler import (
            crawl_all_docs, 
            crawl_pydantic_ai_docs, 
            crawl_langchain_docs,
            crawl_langgraph_docs,
            crawl_anthropic_docs
        )
        from ergon.core.database.engine import get_db_session
        from ergon.core.database.models import DocumentationPage
        
        # Ensure timeout is within bounds (1-600 seconds)
        timeout = max(1, min(600, timeout))
        
        # Initialize database if not exists
        ensure_db_initialized()
        
        # Get current doc count
        with get_db_session() as db:
            initial_doc_count = db.query(DocumentationPage).count()
        
        # Preload documentation based on source
        if source.lower() == "all":
            with console.status("[bold green]Preloading all documentation sources..."):
                pages_crawled = asyncio.run(crawl_all_docs(
                    max_pages=max_pages,
                    max_depth=max_depth,
                    timeout=timeout
                ))
            console.print(f"[bold green]Successfully preloaded {pages_crawled} documentation pages from all sources![/bold green]")
        
        elif source.lower() == "pydantic":
            with console.status("[bold green]Preloading Pydantic documentation..."):
                pages_crawled = asyncio.run(crawl_pydantic_ai_docs(
                    max_pages=max_pages,
                    max_depth=max_depth,
                    timeout=timeout
                ))
            console.print(f"[bold green]Successfully preloaded {pages_crawled} Pydantic documentation pages![/bold green]")
        
        elif source.lower() == "langchain":
            with console.status("[bold green]Preloading LangChain documentation..."):
                pages_crawled = asyncio.run(crawl_langchain_docs(
                    max_pages=max_pages,
                    max_depth=max_depth,
                    timeout=timeout
                ))
            console.print(f"[bold green]Successfully preloaded {pages_crawled} LangChain documentation pages![/bold green]")
        
        elif source.lower() == "langgraph":
            with console.status("[bold green]Preloading LangGraph documentation..."):
                pages_crawled = asyncio.run(crawl_langgraph_docs(
                    max_pages=max_pages,
                    max_depth=max_depth,
                    timeout=timeout
                ))
            console.print(f"[bold green]Successfully preloaded {pages_crawled} LangGraph documentation pages![/bold green]")
        
        elif source.lower() == "anthropic":
            with console.status("[bold green]Preloading Anthropic documentation..."):
                pages_crawled = asyncio.run(crawl_anthropic_docs(
                    max_pages=max_pages,
                    max_depth=max_depth,
                    timeout=timeout
                ))
            console.print(f"[bold green]Successfully preloaded {pages_crawled} Anthropic documentation pages![/bold green]")
        
        else:
            console.print(f"[bold red]Invalid source: {source}[/bold red]")
            console.print("Valid sources: all, pydantic, langchain, langgraph, anthropic")
            raise typer.Exit(1)
        
        # Get updated doc count
        with get_db_session() as db:
            final_doc_count = db.query(DocumentationPage).count()
            new_docs = final_doc_count - initial_doc_count
        
        console.print(f"[bold green]Documentation preloading complete![/bold green]")
        console.print(f"[green]Added {new_docs} new document(s). Total document count: {final_doc_count}[/green]")
        
    except Exception as e:
        console.print(f"[bold red]Error preloading documentation: {str(e)}[/bold red]")
        import traceback
        console.print(f"[dim red]{traceback.format_exc()}[/dim red]")
        raise typer.Exit(1)