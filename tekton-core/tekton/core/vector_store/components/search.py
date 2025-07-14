"""Search Component for Vector Store.

This module provides search functionality for the Vector Store.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union

# Configure logger
logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Search engine for finding documents by vector similarity or keyword matching.
    """

    def __init__(
        self,
        document_store: Any,
        faiss_index: Any,
        keyword_index: Optional[Any] = None,
        embedding_engine: Optional[Any] = None
    ):
        """Initialize the search engine.
        
        Args:
            document_store: Document store component
            faiss_index: FAISS index component
            keyword_index: Optional keyword index component
            embedding_engine: Optional embedding engine component
        """
        self.document_store = document_store
        self.faiss_index = faiss_index
        self.keyword_index = keyword_index
        self.embedding_engine = embedding_engine
        
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        hybrid_alpha: float = 0.5,  # Weight for vector search (1-hybrid_alpha for keyword)
        use_hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for documents by semantic similarity with hybrid search support.
        
        Args:
            query: Query string
            top_k: Number of results to return
            filters: Optional metadata filters
            hybrid_alpha: Weight for vector similarity (0.0-1.0)
            use_hybrid: Whether to use hybrid search
            
        Returns:
            List of matching documents
        """
        try:
            # If no documents, return empty list
            doc_count = self.document_store.count()
            if doc_count == 0:
                return []
                
            # Get more results than requested to allow for filtering
            k_multiplier = 4  # Get 4x results for filtering
            search_k = top_k * k_multiplier
            
            # Limit search_k to the number of documents
            search_k = min(search_k, doc_count)
            
            # If search_k is still 0, return empty results
            if search_k == 0:
                return []
            
            if use_hybrid and self.keyword_index and hybrid_alpha < 1.0:
                # Perform hybrid search (vector + keyword)
                results = self._hybrid_search(query, search_k, filters, hybrid_alpha)
            else:
                # Perform vector-only search
                results = self._vector_search(query, search_k, filters)
            
            # Return top_k results
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
            
    def _vector_search(
        self, 
        query: str, 
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector-based similarity search.
        
        Args:
            query: Query string
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of matching documents
        """
        if not self.embedding_engine:
            logger.error("Embedding engine not available for vector search")
            return []
            
        # Get query embedding
        query_embedding = self.embedding_engine.encode(query)
        
        # Search the index
        distances, indices = self.faiss_index.search(query_embedding, top_k)
        
        # Process results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0:  # Invalid index
                continue
            
            # Find the document with this embedding ID
            doc_id = self.document_store.get_doc_id_by_embedding_id(idx)
            if doc_id is None:
                continue
                
            doc = self.document_store.get(doc_id)
            if not doc:
                continue
            
            # Apply filters if provided
            if filters and not self._matches_filters(doc, filters):
                continue
            
            # Calculate score (convert distance to similarity score)
            distance_metric = self.faiss_index.distance_metric
            if distance_metric == "cosine":
                score = float(distances[0][i])  # Already a similarity score
            else:
                # Convert L2 distance to similarity score (0-1 range)
                distance = float(distances[0][i])
                max_distance = 2.0  # Maximum L2 distance for normalized vectors
                score = 1.0 - (distance / max_distance)
            
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc.get("metadata", {}),
                "score": score,
                "search_type": "vector"
            })
        
        return results
        
    def _keyword_search(
        self, 
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search.
        
        Args:
            query: Query string
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of matching documents
        """
        if not self.keyword_index:
            logger.warning("Keyword index not available")
            return []
            
        # Get keyword matches
        matches = self.keyword_index.search(query, top_k * 2)
        
        # Process results
        results = []
        for embedding_id, match_count in matches:
            # Find the document with this embedding ID
            doc_id = self.document_store.get_doc_id_by_embedding_id(embedding_id)
            if doc_id is None:
                continue
                
            doc = self.document_store.get(doc_id)
            if not doc:
                continue
            
            # Apply filters if provided
            if filters and not self._matches_filters(doc, filters):
                continue
            
            # Calculate score
            total_tokens = self.keyword_index.get_query_token_count(query)
            score = match_count / total_tokens if total_tokens > 0 else 0
            
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc.get("metadata", {}),
                "score": score,
                "search_type": "keyword",
                "match_count": match_count
            })
        
        return results
        
    def _hybrid_search(
        self, 
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
        hybrid_alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector and keyword search.
        
        Args:
            query: Query string
            top_k: Number of results to return
            filters: Optional metadata filters
            hybrid_alpha: Weight for vector similarity (0.0-1.0)
            
        Returns:
            List of matching documents
        """
        # Get vector search results
        vector_results = self._vector_search(query, top_k*2, filters)
        
        # Get keyword search results
        keyword_results = self._keyword_search(query, top_k*2, filters)
        
        # Combine results
        combined_results = {}
        
        # Process vector results
        for result in vector_results:
            doc_id = result["id"]
            combined_results[doc_id] = {
                "id": doc_id,
                "content": result["content"],
                "metadata": result["metadata"],
                "vector_score": result["score"],
                "keyword_score": 0.0,
                "search_type": "hybrid"
            }
        
        # Process keyword results
        for result in keyword_results:
            doc_id = result["id"]
            if doc_id in combined_results:
                # Update existing result
                combined_results[doc_id]["keyword_score"] = result["score"]
            else:
                # Add new result
                combined_results[doc_id] = {
                    "id": doc_id,
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "vector_score": 0.0,
                    "keyword_score": result["score"],
                    "search_type": "hybrid"
                }
        
        # Calculate hybrid scores and sort
        results = []
        for doc_id, result in combined_results.items():
            # Combined score with weighting
            hybrid_score = (hybrid_alpha * result["vector_score"]) + ((1 - hybrid_alpha) * result["keyword_score"])
            result["score"] = hybrid_score
            results.append(result)
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
        
    def _matches_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Enhanced filter matching with support for nested objects and operators.
        
        Args:
            doc: Document to check
            filters: Filters to apply
            
        Returns:
            True if document matches filters
        """
        metadata = doc.get("metadata", {})
        
        for key, value in filters.items():
            # Handle nested paths with dot notation
            if "." in key:
                parts = key.split(".")
                current = metadata
                for part in parts[:-1]:
                    if part not in current or not isinstance(current[part], dict):
                        return False
                    current = current[part]
                final_key = parts[-1]
                if final_key not in current:
                    return False
                field_value = current[final_key]
            else:
                # Regular non-nested field
                if key not in metadata:
                    return False
                field_value = metadata[key]
            
            # Match based on filter type
            if isinstance(value, list):
                # List filter (any match)
                if field_value not in value:
                    return False
            elif isinstance(value, dict):
                # Operator filters (gt, gte, lt, lte, ne, in, nin)
                for op, op_value in value.items():
                    if op == "gt" and not field_value > op_value:
                        return False
                    elif op == "gte" and not field_value >= op_value:
                        return False
                    elif op == "lt" and not field_value < op_value:
                        return False
                    elif op == "lte" and not field_value <= op_value:
                        return False
                    elif op == "ne" and field_value == op_value:  # not equal
                        return False
                    elif op == "in" and field_value not in op_value:  # in list
                        return False
                    elif op == "nin" and field_value in op_value:  # not in list
                        return False
            else:
                # Exact match
                if field_value != value:
                    return False
        
        return True