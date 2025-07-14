"""Keyword Index Component for Vector Store.

This module provides keyword indexing and search functionality for the Vector Store.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union

# Configure logger
logger = logging.getLogger(__name__)


class KeywordIndex:
    """
    Keyword indexing and search functionality for hybrid search.
    """

    def __init__(self, path: str, use_nltk: bool = True):
        """Initialize the keyword index.
        
        Args:
            path: Path to store the index
            use_nltk: Whether to use NLTK for stopwords
        """
        self.path = path
        self.use_nltk = use_nltk
        self.keyword_index_path = os.path.join(path, "keyword_index.json")
        self.keyword_index = {}  # Maps words to document IDs
        
        # Set up stopwords
        self._setup_stopwords()
        
        # Load existing index if available
        self._load()
        
    def _setup_stopwords(self):
        """Set up stopwords for keyword filtering."""
        # Basic stopwords as fallback
        self.stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by"}
        
        # Try to use NLTK for better stopwords
        if self.use_nltk:
            try:
                import nltk
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                from nltk.corpus import stopwords
                self.stopwords = set(stopwords.words('english'))
                logger.info("Using NLTK stopwords for keyword index")
            except:
                logger.warning("Failed to load NLTK stopwords, using basic stopwords")
                
    def _load(self):
        """Load keyword index from disk."""
        if os.path.exists(self.keyword_index_path):
            try:
                with open(self.keyword_index_path, "r") as f:
                    keyword_data = json.load(f)
                    # Convert indices back to sets (JSON serializes them as lists)
                    self.keyword_index = {
                        word: set(indices) for word, indices in keyword_data.items()
                    }
                logger.info(f"Loaded keyword index with {len(self.keyword_index)} entries")
            except Exception as e:
                logger.error(f"Error loading keyword index: {e}")
                self.keyword_index = {}
                
    def save(self):
        """Save keyword index to disk."""
        try:
            # Convert sets to lists for JSON serialization
            serializable_index = {
                word: list(indices) for word, indices in self.keyword_index.items()
            }
            with open(self.keyword_index_path, "w") as f:
                json.dump(serializable_index, f)
            logger.info(f"Saved keyword index with {len(self.keyword_index)} entries")
        except Exception as e:
            logger.error(f"Error saving keyword index: {e}")
            
    def index_document(self, doc_id: str, content: str, embedding_id: int):
        """Index document keywords for hybrid search.
        
        Args:
            doc_id: Document ID
            content: Document content
            embedding_id: Index in the FAISS store
        """
        try:
            # Tokenize content
            tokens = re.findall(r'\b\w+\b', content.lower())
            
            # Remove stopwords and short tokens
            tokens = [token for token in tokens if token not in self.stopwords and len(token) > 2]
            
            # Add to keyword index
            for token in tokens:
                if token not in self.keyword_index:
                    self.keyword_index[token] = set()
                self.keyword_index[token].add(embedding_id)
                
        except Exception as e:
            logger.warning(f"Error indexing keywords for document {doc_id}: {e}")
            
    def remove_document(self, embedding_id: int):
        """Remove document from keyword index.
        
        Args:
            embedding_id: Embedding ID to remove
        """
        # Remove embedding ID from all keyword entries
        for token, indices in list(self.keyword_index.items()):
            if embedding_id in indices:
                indices.remove(embedding_id)
                # Remove token if no documents left
                if not indices:
                    del self.keyword_index[token]
                    
    def search(self, query: str, top_k: int) -> List[Tuple[int, int]]:
        """Search for documents matching query keywords.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            List of tuples (embedding_id, match_count)
        """
        # Tokenize query
        tokens = re.findall(r'\b\w+\b', query.lower())
        
        # Remove stopwords and short tokens
        tokens = [token for token in tokens if token not in self.stopwords and len(token) > 2]
        
        if not tokens:
            return []
        
        # Find documents with matching tokens
        matches = {}
        for token in tokens:
            if token in self.keyword_index:
                for idx in self.keyword_index[token]:
                    matches[idx] = matches.get(idx, 0) + 1
        
        # Sort by number of matching tokens
        sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_matches[:top_k]
        
    def get_query_token_count(self, query: str) -> int:
        """Get number of tokens in query after removing stopwords.
        
        Args:
            query: Query string
            
        Returns:
            Number of tokens
        """
        # Tokenize query
        tokens = re.findall(r'\b\w+\b', query.lower())
        
        # Remove stopwords and short tokens
        tokens = [token for token in tokens if token not in self.stopwords and len(token) > 2]
        
        return len(tokens)
        
    def get_document_tokens(self, content: str) -> List[str]:
        """Get tokens for a document after removing stopwords.
        
        Args:
            content: Document content
            
        Returns:
            List of tokens
        """
        # Tokenize content
        tokens = re.findall(r'\b\w+\b', content.lower())
        
        # Remove stopwords and short tokens
        tokens = [token for token in tokens if token not in self.stopwords and len(token) > 2]
        
        return tokens
        
    def clear(self):
        """Clear the keyword index."""
        self.keyword_index = {}
        
    def count_entries(self) -> int:
        """Count number of entries in keyword index.
        
        Returns:
            Number of entries
        """
        return len(self.keyword_index)
        
    def count_references(self) -> int:
        """Count total number of document references in keyword index.
        
        Returns:
            Number of document references
        """
        return sum(len(indices) for indices in self.keyword_index.values())