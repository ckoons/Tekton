"""
Documentation crawler for Ergon.

This module crawls various documentation sites and indexes
them for use in agent generation.
"""

import os
import re
import json
import asyncio
import httpx
import hashlib
import pickle
from typing import Dict, Any, List, Optional, Set
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin, urlparse
from pathlib import Path

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import DocumentationPage
from ergon.core.vector_store.faiss_store import FAISSDocumentStore
from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class DocumentationCrawler:
    """
    Crawler for collecting and indexing documentation from websites.
    """
    
    def __init__(
        self,
        base_urls: Optional[List[str]] = None,
        max_pages: int = 1000,
        concurrent_requests: int = 10,
        user_agent: str = "Ergon Documentation Crawler"
    ):
        """
        Initialize the documentation crawler.
        
        Args:
            base_urls: List of URLs to start crawling from
            max_pages: Maximum number of pages to crawl
            concurrent_requests: Maximum number of concurrent requests
            user_agent: User agent string for requests
        """
        self.base_urls = base_urls or [
            "https://docs.pydantic.ai/latest/",
            "https://python.langchain.com/docs/",
            "https://docs.anthropic.com/claude/docs/",
            "https://langchain-ai.github.io/langgraph/",
        ]
        self.max_pages = max_pages
        self.concurrent_requests = concurrent_requests
        self.user_agent = user_agent
        
        # Additional configurable parameters
        self.max_depth = 3  # Default max link traversal depth
        self.timeout = 10   # Default HTTP request timeout in seconds
        self.progress_callback = None  # Progress tracking callback function
        
        self.crawled_urls: Set[str] = set()
        self.urls_to_crawl: Set[str] = set(self.base_urls)
        self.vector_store = FAISSDocumentStore()
    
    async def crawl(self) -> List[Dict[str, Any]]:
        """
        Crawl documentation pages.
        
        Returns:
            List of crawled page data
        """
        # Initialize counters
        pages_crawled = 0
        crawled_pages = []
        
        # Initialize HTTP client with configurable timeout
        async with httpx.AsyncClient(
            headers={"User-Agent": self.user_agent},
            follow_redirects=True,
            timeout=float(self.timeout)
        ) as client:
            # Process URLs until queue is empty or max_pages is reached
            while self.urls_to_crawl and pages_crawled < self.max_pages:
                # Take up to concurrent_requests URLs to process
                batch_urls = list(self.urls_to_crawl)[:self.concurrent_requests]
                self.urls_to_crawl -= set(batch_urls)
                
                # Create tasks for batch with depth tracking
                tasks = [self._process_url(client, url, depth=1) for url in batch_urls]
                
                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Error crawling page: {str(result)}")
                        continue
                    
                    if result:
                        crawled_pages.append(result)
                        pages_crawled += 1
                        
                        # Call progress callback if provided
                        if self.progress_callback:
                            self.progress_callback()
                        
                        # Log progress
                        if pages_crawled % 10 == 0:
                            logger.info(f"Crawled {pages_crawled} pages...")
        
        # Log completion
        logger.info(f"Crawl completed. Processed {pages_crawled} pages.")
        
        # Return crawled pages
        return crawled_pages
    
    def _get_cache_path(self, url: str) -> Path:
        """
        Get cache file path for a URL.
        
        Args:
            url: URL to get cache path for
            
        Returns:
            Path to cache file
        """
        # Create cache directory if it doesn't exist
        cache_dir = Path(settings.vector_db_path) / "doc_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a unique filename based on URL
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return cache_dir / f"{url_hash}.pickle"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """
        Check if cache is valid.
        
        Args:
            cache_path: Path to cache file
            
        Returns:
            True if cache is valid, False otherwise
        """
        # Check if cache file exists
        if not cache_path.exists():
            return False
        
        # Check if cache is fresh (less than 1 week old)
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - cache_time
        return age < timedelta(days=7)  # Cache is valid for 1 week
        
    async def _process_url(self, client: httpx.AsyncClient, url: str, depth: int = 1) -> Optional[Dict[str, Any]]:
        """
        Process a single URL.
        
        Args:
            client: HTTP client
            url: URL to process
            depth: Current depth in the crawl
        
        Returns:
            Page data if successful, None otherwise
        """
        # Skip already crawled URLs
        if url in self.crawled_urls:
            return None
        
        # Add to crawled set
        self.crawled_urls.add(url)
        
        # Check cache
        cache_path = self._get_cache_path(url)
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    page_data = pickle.load(f)
                    logger.info(f"Loaded from cache: {url}")
                    
                    # Extract new URLs to crawl (only if we're not at max depth)
                    if depth < self.max_depth and page_data.get("html"):
                        soup = BeautifulSoup(page_data["html"], "html.parser")
                        new_urls = self._extract_urls(soup, url, depth)
                        self.urls_to_crawl.update(new_urls - self.crawled_urls)
                    
                    # Remove HTML from returned data (we only need it for URL extraction)
                    if "html" in page_data:
                        del page_data["html"]
                    
                    return page_data
            except Exception as e:
                logger.error(f"Error loading cache for {url}: {str(e)}")
                # Continue with normal processing if cache loading fails
        
        try:
            # Fetch page
            response = await client.get(url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract title
            title = self._extract_title(soup) or url
            
            # Extract content
            content = self._extract_content(soup)
            
            # Extract new URLs to crawl (only if we're not at max depth)
            if depth < self.max_depth:
                new_urls = self._extract_urls(soup, url, depth)
                self.urls_to_crawl.update(new_urls - self.crawled_urls)
            
            # Extract source
            parsed_url = urlparse(url)
            source = parsed_url.netloc
            
            # Create page data
            page_data = {
                "title": title,
                "content": content,
                "url": url,
                "source": source,
                "depth": depth,
                "crawled_at": datetime.now().isoformat(),
                "html": response.text  # Store HTML for cache
            }
            
            # Save to cache
            with open(cache_path, 'wb') as f:
                pickle.dump(page_data, f)
            
            # Remove HTML from returned data (we only need it for URL extraction and caching)
            del page_data["html"]
            
            return page_data
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract page content."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        
        # Extract main content
        main_content = soup.find("main") or soup.find("article") or soup.find("div", {"class": "content"}) or soup
        
        # Get text and clean it
        text = main_content.get_text()
        
        # Clean text (remove extra whitespace, etc.)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_urls(self, soup: BeautifulSoup, base_url: str, current_depth: int = 1) -> Set[str]:
        """
        Extract URLs to crawl next.
        
        Args:
            soup: Beautiful Soup object
            base_url: Current URL being processed
            current_depth: Current crawl depth
        
        Returns:
            Set of URLs to crawl next
        """
        # Don't extract more URLs if we've reached max depth
        if current_depth >= self.max_depth:
            return set()
            
        urls = set()
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            
            # Skip empty links, anchors, or javascript
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue
            
            # Resolve relative URLs
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            
            # Only include URLs from the same domain
            if parsed_url.netloc == base_domain:
                # Normalize URL (remove fragments)
                normalized_url = parsed_url._replace(fragment="").geturl()
                urls.add(normalized_url)
        
        return urls
    
    async def crawl_and_index(self) -> int:
        """
        Crawl documentation and store in database and vector store.
        
        Returns:
            Number of pages indexed
        """
        # Crawl pages
        crawled_pages = await self.crawl()
        
        # Store in database and vector store
        with get_db_session() as db:
            for page_data in crawled_pages:
                # Create database record
                doc_page = DocumentationPage(
                    title=page_data["title"],
                    content=page_data["content"],
                    url=page_data["url"],
                    source=page_data["source"],
                )
                db.add(doc_page)
                db.commit()
                db.refresh(doc_page)
                
                # Add to vector store
                doc_id = self.vector_store.add_documents([{
                    "id": f"doc_{doc_page.id}",
                    "content": page_data["content"],
                    "metadata": {
                        "title": page_data["title"],
                        "url": page_data["url"],
                        "source": page_data["source"],
                    }
                }])[0]
                
                # Update database record with vector ID
                doc_page.embedding_id = doc_id
                db.commit()
        
        return len(crawled_pages)


async def crawl_pydantic_ai_docs(max_pages=200, max_depth=3, timeout=30, progress_callback=None):
    """Crawl Pydantic AI documentation only."""
    crawler = DocumentationCrawler(
        base_urls=["https://docs.pydantic.ai/latest/"],
        max_pages=max_pages
    )
    # Configure crawler with additional parameters
    crawler.max_depth = max_depth
    # Set timeout for HTTP requests
    crawler.timeout = timeout
    # Set progress callback
    crawler.progress_callback = progress_callback
    return await crawler.crawl_and_index()


async def crawl_langchain_docs(max_pages=200, max_depth=3, timeout=30, progress_callback=None):
    """Crawl LangChain documentation only."""
    crawler = DocumentationCrawler(
        base_urls=["https://python.langchain.com/docs/"],
        max_pages=max_pages
    )
    # Configure crawler with additional parameters
    crawler.max_depth = max_depth
    # Set timeout for HTTP requests
    crawler.timeout = timeout
    # Set progress callback
    crawler.progress_callback = progress_callback
    return await crawler.crawl_and_index()


async def crawl_anthropic_docs(max_pages=200, max_depth=3, timeout=30, progress_callback=None):
    """Crawl Anthropic documentation only."""
    crawler = DocumentationCrawler(
        base_urls=["https://docs.anthropic.com/claude/docs/"],
        max_pages=max_pages
    )
    # Configure crawler with additional parameters
    crawler.max_depth = max_depth
    # Set timeout for HTTP requests
    crawler.timeout = timeout
    # Set progress callback
    crawler.progress_callback = progress_callback
    return await crawler.crawl_and_index()


async def crawl_langgraph_docs(max_pages=200, max_depth=3, timeout=30, progress_callback=None):
    """Crawl LangGraph documentation only."""
    crawler = DocumentationCrawler(
        base_urls=["https://langchain-ai.github.io/langgraph/"],
        max_pages=max_pages
    )
    # Configure crawler with additional parameters
    crawler.max_depth = max_depth
    # Set timeout for HTTP requests
    crawler.timeout = timeout
    # Set progress callback
    crawler.progress_callback = progress_callback
    return await crawler.crawl_and_index()


async def crawl_all_docs(max_pages=200, max_depth=3, timeout=30, progress_callback=None):
    """Crawl all documentation."""
    crawler = DocumentationCrawler(max_pages=max_pages)
    # Configure crawler with additional parameters
    crawler.max_depth = max_depth
    # Set timeout for HTTP requests
    crawler.timeout = timeout
    # Set progress callback
    crawler.progress_callback = progress_callback
    return await crawler.crawl_and_index()
