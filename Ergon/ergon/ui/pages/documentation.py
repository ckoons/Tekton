"""
Documentation management page for Ergon.

This page allows users to preload documentation from various sources
and search indexed documentation.
"""

import streamlit as st
import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx
import time
from datetime import datetime

from ergon.core.docs.crawler import (
    crawl_pydantic_ai_docs,
    crawl_langchain_docs,
    crawl_anthropic_docs,
    crawl_langgraph_docs,
    crawl_all_docs
)
from ergon.core.database.engine import get_db_session
from ergon.core.database.models import DocumentationPage
from ergon.core.vector_store.faiss_store import FAISSDocumentStore
from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))

def documentation_page():
    """Render the documentation management page."""
    st.title("Documentation Management")
    st.markdown("Manage documentation sources for use with Ergon agents")
    
    # Create tabs for different functionality
    tab1, tab2, tab3 = st.tabs(["Preload Documentation", "Search Documentation", "Custom Documentation"])
    
    # Tab 1: Preload Documentation
    with tab1:
        st.header("Preload Documentation")
        st.markdown("""
        Preload documentation from popular AI frameworks and tools to enhance your agents' knowledge.
        Documentation is chunked and stored in a vector database for efficient semantic search.
        """)
        
        # Documentation sources with descriptions
        sources = {
            "pydantic": {
                "name": "Pydantic",
                "description": "Data validation and parsing library used for type hints and data schemas",
                "url": "https://docs.pydantic.ai/latest/",
                "icon": "📝",
                "function": crawl_pydantic_ai_docs
            },
            "langchain": {
                "name": "LangChain",
                "description": "Framework for developing applications with LLMs through composability",
                "url": "https://python.langchain.com/docs/",
                "icon": "🦜",
                "function": crawl_langchain_docs
            },
            "anthropic": {
                "name": "Anthropic (Claude)",
                "description": "Documentation for Claude AI models, including API, best practices, and examples",
                "url": "https://docs.anthropic.com/claude/docs/",
                "icon": "🧠",
                "function": crawl_anthropic_docs
            },
            "langgraph": {
                "name": "LangGraph",
                "description": "Framework for creating stateful, multi-actor applications with LLMs",
                "url": "https://langchain-ai.github.io/langgraph/",
                "icon": "📊",
                "function": crawl_langgraph_docs
            },
            "all": {
                "name": "All Sources",
                "description": "Crawl all documentation sources listed above",
                "url": "",
                "icon": "🔍",
                "function": crawl_all_docs
            }
        }
        
        # Create columns for documentation sources
        col1, col2 = st.columns(2)
        
        # Column 1 - Sources
        with col1:
            st.subheader("Select Documentation Source")
            selected_source = st.radio(
                "Documentation Source",
                list(sources.keys()),
                format_func=lambda x: f"{sources[x]['icon']} {sources[x]['name']}"
            )
            
            # Show description for selected source
            st.info(sources[selected_source]["description"])
            
            if selected_source != "all":
                st.markdown(f"Source URL: [{sources[selected_source]['url']}]({sources[selected_source]['url']})")
            
            # Configure crawl parameters
            st.subheader("Crawl Configuration")
            
            max_pages = st.slider(
                "Maximum Pages",
                min_value=10,
                max_value=500,
                value=200,
                step=10,
                help="Maximum number of pages to crawl"
            )
            
            max_depth = st.slider(
                "Maximum Depth",
                min_value=1,
                max_value=5,
                value=3,
                step=1,
                help="Maximum link depth to follow from starting page"
            )
            
            timeout = st.slider(
                "Timeout (seconds)",
                min_value=10,
                max_value=600,
                value=30,
                step=10,
                help="Timeout for HTTP requests in seconds"
            )
        
        # Column 2 - Status and Actions
        with col2:
            st.subheader("Documentation Status")
            
            # Get current documentation stats
            with get_db_session() as db:
                doc_count = db.query(DocumentationPage).count()
                
                # Get counts by source
                source_counts = {}
                for source in ["pydantic", "langchain", "anthropic", "langgraph"]:
                    source_counts[source] = db.query(DocumentationPage).filter(
                        DocumentationPage.source.contains(source)
                    ).count()
                
                # Get most recent document
                most_recent = db.query(DocumentationPage).order_by(
                    DocumentationPage.created_at.desc()
                ).first()
                
                if most_recent:
                    last_updated = most_recent.created_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    last_updated = "Never"
            
            # Display stats
            st.metric("Total Documents", doc_count)
            st.write("Documents by Source:")
            for source, count in source_counts.items():
                st.write(f"- {sources[source]['icon']} {sources[source]['name']}: {count}")
            
            st.write(f"Last Updated: {last_updated}")
            
            # Start crawl button
            if st.button("Start Crawling", type="primary", use_container_width=True):
                # Progress placeholder
                progress_placeholder = st.empty()
                progress_bar = progress_placeholder.progress(0)
                status_area = st.empty()
                
                # Progress callback
                def progress_callback(current, total, message=None):
                    progress = min(current / max(total, 1), 1.0)
                    progress_bar.progress(progress)
                    if message:
                        status_area.write(message)
                
                # Run the crawl in background
                try:
                    status_area.write(f"Starting documentation crawl for {sources[selected_source]['name']}...")
                    
                    # Create and run the async task
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    crawl_function = sources[selected_source]["function"]
                    result = loop.run_until_complete(
                        crawl_function(
                            max_pages=max_pages,
                            max_depth=max_depth,
                            timeout=timeout,
                            progress_callback=progress_callback
                        )
                    )
                    loop.close()
                    
                    # Update UI with results
                    progress_bar.progress(1.0)
                    status_area.success(f"Crawl complete! Indexed {result} pages from {sources[selected_source]['name']}.")
                    
                    # Add a rerun button to refresh the stats
                    if st.button("Refresh Stats"):
                        st.experimental_rerun()
                    
                except Exception as e:
                    status_area.error(f"Error during crawl: {str(e)}")
    
    # Tab 2: Search Documentation
    with tab2:
        st.header("Search Documentation")
        st.markdown("""
        Search the indexed documentation to find relevant information.
        The search uses semantic similarity to find the most relevant documents.
        """)
        
        # Search interface
        search_query = st.text_input("Search Query", placeholder="Enter search terms...")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Source filter
            source_options = ["All Sources"] + [sources[s]["name"] for s in sources if s != "all"]
            selected_source_filter = st.selectbox("Filter by Source", source_options)
        
        with col2:
            # Results count
            num_results = st.slider(
                "Number of Results",
                min_value=3,
                max_value=20,
                value=5,
                step=1
            )
        
        # Search button
        if st.button("Search Documentation", use_container_width=True) and search_query:
            with st.spinner("Searching..."):
                # Convert selected source to filter value
                source_filter = None
                if selected_source_filter != "All Sources":
                    # Convert display name back to key
                    for k, v in sources.items():
                        if v["name"] == selected_source_filter:
                            source_filter = k
                            break
                
                # Perform search using vector store
                vector_store = FAISSDocumentStore()
                search_results = vector_store.search(
                    search_query,
                    limit=num_results,
                    metadata_filter={"source": source_filter} if source_filter else None
                )
                
                # Display results
                if search_results:
                    st.success(f"Found {len(search_results)} results")
                    
                    for i, result in enumerate(search_results, 1):
                        with st.expander(f"{i}. {result['metadata'].get('title', 'Untitled Document')}"):
                            st.markdown(f"**Source:** {result['metadata'].get('source', 'Unknown')}")
                            st.markdown(f"**URL:** [{result['metadata'].get('url', '#')}]({result['metadata'].get('url', '#')})")
                            st.markdown(f"**Relevance Score:** {result['score']:.2f}")
                            st.markdown("**Content:**")
                            st.markdown(result["content"])
                else:
                    st.warning("No results found. Try a different search query.")
    
    # Tab 3: Custom Documentation
    with tab3:
        st.header("Add Custom Documentation")
        st.markdown("""
        Add custom documentation by providing a URL to crawl or by directly
        pasting document text for indexing.
        """)
        
        # Create tabs for different input methods
        input_tab1, input_tab2 = st.tabs(["Crawl URL", "Direct Input"])
        
        # URL Crawl tab
        with input_tab1:
            st.subheader("Crawl URL")
            
            custom_url = st.text_input(
                "URL to Crawl",
                placeholder="https://example.com/docs/",
                help="Enter a URL to crawl for documentation"
            )
            
            custom_source = st.text_input(
                "Source Name",
                placeholder="Example Docs",
                help="Name to categorize this documentation"
            )
            
            # URL crawl options
            col1, col2 = st.columns(2)
            
            with col1:
                custom_max_pages = st.slider(
                    "Maximum Pages (URL)",
                    min_value=1,
                    max_value=100,
                    value=10,
                    step=1
                )
                
                custom_max_depth = st.slider(
                    "Maximum Depth (URL)",
                    min_value=1,
                    max_value=3,
                    value=2,
                    step=1
                )
            
            with col2:
                custom_timeout = st.slider(
                    "Timeout (URL)",
                    min_value=5,
                    max_value=60,
                    value=10,
                    step=5
                )
            
            # Crawl button
            if st.button("Crawl URL", use_container_width=True) and custom_url and custom_source:
                # Validate URL
                if not custom_url.startswith("http"):
                    st.error("URL must start with http:// or https://")
                else:
                    with st.spinner("Crawling..."):
                        try:
                            # Create a DocumentationCrawler directly
                            from ergon.core.docs.crawler import DocumentationCrawler
                            
                            crawler = DocumentationCrawler(
                                base_urls=[custom_url],
                                max_pages=custom_max_pages
                            )
                            crawler.max_depth = custom_max_depth
                            crawler.timeout = custom_timeout
                            
                            # Create and run the async task
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            # Override source with custom source
                            original_process_url = crawler._process_url
                            
                            async def custom_process_url(client, url, depth):
                                result = await original_process_url(client, url, depth)
                                if result and isinstance(result, dict):
                                    result["source"] = custom_source
                                return result
                            
                            crawler._process_url = custom_process_url
                            
                            result = loop.run_until_complete(crawler.crawl_and_index())
                            loop.close()
                            
                            st.success(f"Crawl complete! Indexed {result} pages from {custom_source}.")
                            
                        except Exception as e:
                            st.error(f"Error during crawl: {str(e)}")
        
        # Direct Input tab
        with input_tab2:
            st.subheader("Direct Document Input")
            
            direct_title = st.text_input(
                "Document Title",
                placeholder="My Custom Document",
                help="Title for the document"
            )
            
            direct_source = st.text_input(
                "Source Name (Direct)",
                placeholder="Custom Docs",
                help="Name to categorize this documentation"
            )
            
            direct_url = st.text_input(
                "URL (Optional)",
                placeholder="https://example.com/docs/page.html",
                help="Optional URL reference for this document"
            )
            
            direct_content = st.text_area(
                "Document Content",
                placeholder="Paste document content here...",
                height=300,
                help="The content to index"
            )
            
            # Submit button
            if st.button("Add Document", use_container_width=True) and direct_title and direct_source and direct_content:
                with st.spinner("Adding document..."):
                    try:
                        # Store in database
                        with get_db_session() as db:
                            # Create database record
                            doc_page = DocumentationPage(
                                title=direct_title,
                                content=direct_content,
                                url=direct_url or f"direct_input_{datetime.now().isoformat()}",
                                source=direct_source,
                            )
                            db.add(doc_page)
                            db.commit()
                            db.refresh(doc_page)
                            
                            # Add to vector store
                            vector_store = FAISSDocumentStore()
                            doc_id = vector_store.add_documents([{
                                "id": f"doc_{doc_page.id}",
                                "content": direct_content,
                                "metadata": {
                                    "title": direct_title,
                                    "url": direct_url or "",
                                    "source": direct_source,
                                }
                            }])[0]
                            
                            # Update database record with vector ID
                            doc_page.embedding_id = doc_id
                            db.commit()
                        
                        st.success(f"Document '{direct_title}' added successfully!")
                        
                    except Exception as e:
                        st.error(f"Error adding document: {str(e)}")