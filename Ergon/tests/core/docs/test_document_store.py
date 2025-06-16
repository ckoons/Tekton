"""
Tests for document store module.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
import json
import asyncio

from ergon.core.database.engine import get_db_session, init_db
from ergon.core.database.models import DocumentationPage
from ergon.core.docs.document_store import DocumentStore
from ergon.core.vector_store.faiss_store import FAISSDocumentStore
from ergon.utils.config.settings import settings


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_vector_store(temp_dir):
    """Create a temporary vector store."""
    vector_store_path = os.path.join(temp_dir, "vector_store")
    os.makedirs(vector_store_path, exist_ok=True)
    return FAISSDocumentStore(path=vector_store_path)


@pytest.fixture
def temp_db(temp_dir):
    """Create a temporary database."""
    # Save original database URL
    original_db_url = settings.database_url
    
    # Create temporary database path
    temp_db_path = os.path.join(temp_dir, "test.db")
    
    # Set database URL to temporary database
    settings.database_url = f"sqlite:///{temp_db_path}"
    
    # Initialize database
    init_db()
    
    yield
    
    # Reset database URL
    settings.database_url = original_db_url


@pytest.fixture
def doc_store(temp_dir, temp_db):
    """Create a document store."""
    return DocumentStore(vector_store_path=os.path.join(temp_dir, "vector_store"))


def test_document_store_initialization(doc_store):
    """Test document store initialization."""
    assert doc_store is not None
    assert doc_store.vector_store is not None
    assert doc_store.rag is not None


def test_add_documentation(doc_store):
    """Test adding documentation."""
    # Add a documentation page
    doc_id = asyncio.run(doc_store.add_documentation(
        title="Test Documentation",
        content="This is a test documentation page.",
        url="https://example.com/test",
        source="test"
    ))
    
    # Verify document was added to the database
    with get_db_session() as db:
        doc = db.query(DocumentationPage).filter(DocumentationPage.title == "Test Documentation").first()
        assert doc is not None
        assert doc.content == "This is a test documentation page."
        assert doc.url == "https://example.com/test"
        assert doc.source == "test"
    
    # Verify document was added to the vector store
    assert doc_store.vector_store.get_document(f"doc_{doc.id}") is not None


def test_search_documentation(doc_store):
    """Test searching documentation."""
    # Add documentation pages
    asyncio.run(doc_store.add_documentation(
        title="Python Programming",
        content="Python is a high-level programming language known for its readability and simplicity.",
        source="python_docs"
    ))
    
    asyncio.run(doc_store.add_documentation(
        title="JavaScript Basics",
        content="JavaScript is a scripting language primarily used for web development.",
        source="js_docs"
    ))
    
    # Search for Python-related documentation
    results = asyncio.run(doc_store.search_documentation("Python programming language"))
    
    # Verify Python documentation was found
    assert len(results) > 0
    assert any("Python" in result["content"] for result in results)
    
    # Search for JavaScript-related documentation
    results = asyncio.run(doc_store.search_documentation("JavaScript for web"))
    
    # Verify JavaScript documentation was found
    assert len(results) > 0
    assert any("JavaScript" in result["content"] for result in results)


def test_get_relevant_documentation(doc_store):
    """Test getting relevant documentation."""
    # Add documentation pages
    asyncio.run(doc_store.add_documentation(
        title="Machine Learning",
        content="Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.",
        source="ai_docs"
    ))
    
    asyncio.run(doc_store.add_documentation(
        title="Deep Learning",
        content="Deep learning is a subset of machine learning that uses neural networks with many layers.",
        source="ai_docs"
    ))
    
    # Get relevant documentation for a query
    docs = asyncio.run(doc_store.get_relevant_documentation("How do neural networks work?"))
    
    # Verify documentation was found and properly formatted
    assert docs is not None
    assert "neural networks" in docs.lower() or "deep learning" in docs.lower()
    assert "Document 1" in docs  # Formatted output includes document numbers


def test_augment_prompt(doc_store):
    """Test augmenting a prompt with relevant documentation."""
    # Add documentation pages
    asyncio.run(doc_store.add_documentation(
        title="API Development",
        content="RESTful APIs are stateless and separate the client and server implementations.",
        source="api_docs"
    ))
    
    # Original prompt
    original_prompt = "Create a function to build an API endpoint."
    
    # Augment the prompt
    augmented_prompt = asyncio.run(doc_store.augment_prompt(original_prompt, "RESTful API best practices"))
    
    # Verify prompt was augmented
    assert len(augmented_prompt) > len(original_prompt)
    assert original_prompt in augmented_prompt
    assert "API" in augmented_prompt and "stateless" in augmented_prompt


def test_no_relevant_documentation(doc_store):
    """Test behavior when no relevant documentation is found."""
    # Query with no matching documentation
    docs = asyncio.run(doc_store.get_relevant_documentation("quantum computing superposition theory"))
    
    # Verify appropriate response when no documents are found
    assert docs == "No relevant documentation found."
    
    # Test prompt augmentation with no relevant docs
    original_prompt = "Explain quantum computing."
    augmented_prompt = asyncio.run(doc_store.augment_prompt(original_prompt, "quantum computing"))
    
    # Verify original prompt is returned unchanged
    assert augmented_prompt == original_prompt