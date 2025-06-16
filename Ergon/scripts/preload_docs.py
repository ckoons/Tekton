#!/usr/bin/env python3
"""
Preload documentation script for Ergon Docker image.

This script is used to pre-crawl and index documentation from
Pydantic, LangChain, LangGraph, and Anthropic during Docker image build.
"""

import asyncio
import logging
import os
import sys

# Add parent directory to path so we can import ergon modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ergon.core.docs.crawler import (
    crawl_pydantic_ai_docs,
    crawl_langchain_docs,
    crawl_anthropic_docs,
    crawl_langgraph_docs
)
from ergon.core.database.engine import init_db
from ergon.utils.config.settings import settings

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def preload_all_docs():
    """Preload all documentation sources."""
    
    logger.info("Initializing database if needed...")
    if not os.path.exists(settings.database_url.replace("sqlite:///", "")):
        init_db()
    
    logger.info("Starting documentation preloading...")
    
    # Crawl Pydantic docs
    logger.info("Crawling Pydantic documentation...")
    pydantic_pages = await crawl_pydantic_ai_docs(max_pages=300, max_depth=3, timeout=600)  # 10 minute timeout
    logger.info(f"Indexed {pydantic_pages} Pydantic documentation pages")
    
    # Crawl LangChain docs
    logger.info("Crawling LangChain documentation...")
    langchain_pages = await crawl_langchain_docs(max_pages=300, max_depth=3, timeout=600)  # 10 minute timeout
    logger.info(f"Indexed {langchain_pages} LangChain documentation pages")
    
    # Crawl LangGraph docs
    logger.info("Crawling LangGraph documentation...")
    langgraph_pages = await crawl_langgraph_docs(max_pages=300, max_depth=3, timeout=600)  # 10 minute timeout
    logger.info(f"Indexed {langgraph_pages} LangGraph documentation pages")
    
    # Crawl Anthropic docs
    logger.info("Crawling Anthropic documentation...")
    anthropic_pages = await crawl_anthropic_docs(max_pages=300, max_depth=3, timeout=600)  # 10 minute timeout
    logger.info(f"Indexed {anthropic_pages} Anthropic documentation pages")
    
    total_pages = pydantic_pages + langchain_pages + langgraph_pages + anthropic_pages
    logger.info(f"Documentation preloading complete. Total pages indexed: {total_pages}")
    
    return total_pages

if __name__ == "__main__":
    asyncio.run(preload_all_docs())