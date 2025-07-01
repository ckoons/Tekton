#!/usr/bin/env python3
"""
Vector-based Memory Storage

Provides high performance vector-based storage and retrieval 
with semantic search capabilities.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from engram.core.memory.utils import (
    generate_memory_id, 
    format_content,
    load_json_file,
    save_json_file
)

logger = logging.getLogger("engram.memory.vector_storage")

class VectorStorage:
    """
    Vector-based memory storage implementation.
    
    Provides semantically meaningful search capabilities with
    vector embeddings and dimensions reduction for memory retrieval.
    """
    
    def __init__(self, 
                client_id: str, 
                data_dir: Path,
                vector_model: Any,
                vector_db_name: str = "faiss"):
        """
        Initialize vector-based memory storage.
        
        Args:
            client_id: Unique identifier for the client
            data_dir: Directory to store memory data
            vector_model: Model for generating embeddings
            vector_db_name: Name of vector database to use
        """
        self.client_id = client_id
        self.data_dir = data_dir
        self.vector_model = vector_model
        self.vector_db_name = vector_db_name
        self.vector_dim = vector_model.get_sentence_embedding_dimension()
        
        # Initialize vector database
        self.vector_client = None
        self.namespace_collections = {}
        self.vector_db_path = self.data_dir / "vector_db"
        self._initialize_vector_db()
        
    def _initialize_vector_db(self) -> None:
        """Initialize the vector database client and collections."""
        # Create vector DB path
        vector_db_path = self.data_dir / "vector_db"
        vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize based on vector DB type
        if self.vector_db_name == "faiss":
            self._initialize_faiss(vector_db_path)
        elif self.vector_db_name == "chromadb":
            self._initialize_chromadb(vector_db_path)
        elif self.vector_db_name == "lancedb":
            self._initialize_lancedb(vector_db_path)
        elif self.vector_db_name == "qdrant":
            # Qdrant has version compatibility issues - not recommended
            logger.warning("Qdrant has known compatibility issues. Consider using ChromaDB or LanceDB instead.")
            self._initialize_qdrant(vector_db_path)
        else:
            raise ValueError(f"Unsupported vector database: {self.vector_db_name}")
            
    def _initialize_faiss(self, vector_db_path: Path) -> None:
        """Initialize FAISS vector database."""
        try:
            import faiss
            from engram.core.vector_store import VectorStore
            
            # Initialize FAISS vector store
            logger.info("Initializing FAISS vector database")
            
            # TODO: Implement proper FAISS integration
            # This is a placeholder for actual FAISS setup
            self.vector_client = VectorStore(str(vector_db_path))
            
            logger.info("FAISS vector database initialized")
        except ImportError as e:
            logger.error(f"Could not initialize FAISS: {e}")
            raise
    
    def _initialize_chromadb(self, vector_db_path: Path) -> None:
        """Initialize ChromaDB vector database."""
        try:
            import chromadb
            
            # Initialize ChromaDB client
            logger.info("Initializing ChromaDB vector database")
            self.vector_client = chromadb.PersistentClient(path=str(vector_db_path))
            
            logger.info("ChromaDB vector database initialized")
        except ImportError as e:
            logger.error(f"Could not initialize ChromaDB: {e}")
            raise
    
    def _initialize_qdrant(self, vector_db_path: Path) -> None:
        """Initialize Qdrant vector database."""
        try:
            import qdrant_client
            
            # Initialize Qdrant client
            logger.info("Initializing Qdrant vector database")
            
            try:
                # For newer client versions
                self.vector_client = qdrant_client.QdrantClient(path=str(vector_db_path))
            except TypeError:
                # For older client versions
                self.vector_client = qdrant_client.QdrantClient(location=str(vector_db_path))
                
            # Patch validation method to avoid strict_mode_config issues
            if hasattr(self.vector_client, '_validate_collection_info'):
                self._patch_qdrant_validation()
                
            logger.info("Qdrant vector database initialized")
        except ImportError as e:
            logger.error(f"Could not initialize Qdrant: {e}")
            raise
            
    def _patch_qdrant_validation(self) -> None:
        """Patch Qdrant validation to avoid strict_mode_config issues."""
        try:
            # Store original validation method
            self._original_validate = self.vector_client._validate_collection_info
            
            # Create patched method
            def patched_validate(*args, **kwargs):
                # Skip validation to avoid strict_mode_config issues
                return True
                
            # Apply patch
            self.vector_client._validate_collection_info = patched_validate
            logger.info("Applied patch for Qdrant collection validation")
        except Exception as e:
            logger.warning(f"Failed to patch Qdrant validation method: {e}")
            
    def _restore_qdrant_validation(self) -> None:
        """Restore original Qdrant validation method."""
        if hasattr(self, '_original_validate'):
            self.vector_client._validate_collection_info = self._original_validate
    
    def _initialize_lancedb(self, vector_db_path: Path) -> None:
        """Initialize LanceDB vector database."""
        try:
            import lancedb
            
            # Initialize LanceDB client
            logger.info("Initializing LanceDB vector database")
            self.vector_client = lancedb.connect(str(vector_db_path))
            
            logger.info("LanceDB vector database initialized")
        except ImportError as e:
            logger.error(f"Could not initialize LanceDB: {e}")
            raise
            
    def ensure_collection(self, namespace: str) -> bool:
        """
        Ensure collection exists for namespace.
        
        Args:
            namespace: The namespace to create collection for
            
        Returns:
            True if collection exists or was created, False on error
        """
        try:
            collection_name = f"engram-{self.client_id}-{namespace}"
            
            # Check if we've already initialized this collection
            if namespace in self.namespace_collections:
                return True
                
            # Different handling based on vector DB
            if self.vector_db_name == "chromadb":
                # ChromaDB implementation
                collection = self.vector_client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=None  # We'll provide embeddings explicitly
                )
                logger.info(f"Retrieved or created collection {collection_name}")
                
            elif self.vector_db_name == "qdrant":
                # Qdrant implementation
                # Apply patch for validation if needed
                self._patch_qdrant_validation()
                
                # Check if collection exists
                collections = self.vector_client.get_collections().collections
                collection_names = [c.name for c in collections]
                
                if collection_name not in collection_names:
                    # Create new collection
                    try:
                        # Try with dimension parameter first (newer clients)
                        self.vector_client.create_collection(
                            collection_name=collection_name,
                            dimension=self.vector_dim
                        )
                        logger.info(f"Created collection {collection_name} using dimension parameter")
                    except Exception as e:
                        logger.debug(f"First attempt failed: {e}")
                        try:
                            # Try with dictionary config
                            self.vector_client.create_collection(
                                collection_name=collection_name,
                                vectors_config={
                                    "size": self.vector_dim,
                                    "distance": "Cosine"
                                }
                            )
                            logger.info(f"Created collection {collection_name} using dictionary config")
                        except Exception as e2:
                            logger.error(f"Failed to create collection {collection_name}: {e2}")
                            self._restore_qdrant_validation()
                            return False
                
                # Restore original validation
                self._restore_qdrant_validation()
                
            elif self.vector_db_name == "faiss":
                # FAISS implementation - collections are handled by VectorStore
                pass
                
            elif self.vector_db_name == "lancedb":
                # LanceDB implementation
                try:
                    # Check if table exists
                    existing_tables = self.vector_client.table_names()
                    if collection_name not in existing_tables:
                        # Create new table with schema
                        import pyarrow as pa
                        schema = pa.schema([
                            pa.field("id", pa.string()),
                            pa.field("content", pa.string()),
                            pa.field("vector", pa.list_(pa.float32(), self.vector_dim)),
                            pa.field("metadata", pa.string())  # JSON string
                        ])
                        self.vector_client.create_table(collection_name, schema=schema)
                        logger.info(f"Created LanceDB table {collection_name}")
                except Exception as e:
                    logger.error(f"Failed to create LanceDB table {collection_name}: {e}")
                    return False
                    
            else:
                raise ValueError(f"Unknown vector database: {self.vector_db_name}")
                
            # Store collection name for future use
            self.namespace_collections[namespace] = collection_name
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring collection for namespace {namespace}: {e}")
            return False
            
    def add(self, 
           content: Union[str, List[Dict[str, str]]],
           namespace: str,
           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory to vector storage.
        
        Args:
            content: The memory content (string or message objects)
            namespace: The namespace to store in
            metadata: Optional metadata for the memory
            
        Returns:
            Boolean indicating success
        """
        # Ensure collection exists
        if not self.ensure_collection(namespace):
            logger.error(f"Failed to ensure collection for namespace {namespace}")
            return False
            
        # Get collection name
        collection_name = self.namespace_collections.get(namespace)
        if not collection_name:
            logger.error(f"No collection found for namespace: {namespace}")
            return False
            
        # Format content to string if needed
        content_str = format_content(content)
        
        # Generate a unique memory ID
        memory_id = generate_memory_id(namespace, content_str)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
            
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["client_id"] = self.client_id
        metadata["namespace"] = namespace
        
        try:
            # Generate embedding for the content
            embedding = self.vector_model.encode(content_str)
            
            # Store based on vector DB type
            if self.vector_db_name == "chromadb":
                # ChromaDB implementation
                collection = self.vector_client.get_collection(name=collection_name)
                
                # Add the document with its embedding
                collection.add(
                    ids=[memory_id],
                    embeddings=[embedding.tolist()],
                    documents=[content_str],
                    metadatas=[{
                        "id": memory_id,
                        "timestamp": metadata.get("timestamp", ""),
                        "client_id": metadata.get("client_id", ""),
                        "namespace": namespace
                    }]
                )
                
                logger.debug(f"Added memory to ChromaDB in namespace {namespace} with ID {memory_id}")
                return True
                
            elif self.vector_db_name == "qdrant":
                # Qdrant implementation
                try:
                    # Try with the newer API style
                    from qdrant_client.http import models
                    self.vector_client.upsert(
                        collection_name=collection_name,
                        points=[
                            models.PointStruct(
                                id=hash(memory_id) % (2**63-1),  # Ensure it's a valid ID
                                vector=embedding.tolist(),
                                payload={
                                    "id": memory_id,
                                    "content": content_str,
                                    "metadata": metadata
                                }
                            )
                        ]
                    )
                except (ImportError, AttributeError):
                    # Fall back to simpler API style
                    self.vector_client.upsert(
                        collection_name=collection_name,
                        points=[{
                            "id": hash(memory_id) % (2**63-1),
                            "vector": embedding.tolist(),
                            "payload": {
                                "id": memory_id,
                                "content": content_str,
                                "metadata": metadata
                            }
                        }]
                    )
                
                logger.debug(f"Added memory to Qdrant in namespace {namespace} with ID {memory_id}")
                return True
                
            elif self.vector_db_name == "faiss":
                # FAISS implementation using the VectorStore
                from engram.core.vector_store import VectorStore
                
                # Ensure we have a VectorStore instance
                if not hasattr(self, '_faiss_store'):
                    # Initialize FAISS store if not already done
                    vector_path = os.path.join(self.vector_db_path, "faiss_vectors")
                    self._faiss_store = VectorStore(
                        data_path=vector_path,
                        dimension=self.embedding_model.get_sentence_embedding_dimension()
                    )
                
                # Use namespace as compartment name
                compartment = namespace
                
                # Add the content with metadata
                metadata_with_id = metadata.copy() if metadata else {}
                metadata_with_id['memory_id'] = memory_id
                metadata_with_id['namespace'] = namespace
                metadata_with_id['created_at'] = datetime.utcnow().isoformat()
                
                # Add to FAISS store
                ids = self._faiss_store.add(
                    compartment=compartment,
                    texts=[content_str],
                    metadatas=[metadata_with_id]
                )
                
                # Save the compartment
                self._faiss_store.save(compartment)
                
                logger.debug(f"Added memory to FAISS in namespace {namespace} with ID {memory_id}")
                return True
                
            elif self.vector_db_name == "lancedb":
                # LanceDB implementation
                import pyarrow as pa
                import pandas as pd
                table = self.vector_client.open_table(collection_name)
                
                # Create pandas DataFrame for LanceDB
                data = pd.DataFrame({
                    "id": [memory_id],
                    "content": [content_str],
                    "vector": [embedding.tolist()],
                    "metadata": [json.dumps(metadata or {})]
                })
                
                table.add(data)
                logger.debug(f"Added memory to LanceDB in namespace {namespace} with ID {memory_id}")
                return True
                
            else:
                raise ValueError(f"Unknown vector database: {self.vector_db_name}")
                
        except Exception as e:
            logger.error(f"Error adding memory to vector database: {e}")
            return False
            
    def search(self,
              query: str,
              namespace: str,
              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories based on a query.
        
        Args:
            query: The search query
            namespace: The namespace to search in
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory objects
        """
        # Ensure collection exists
        if not self.ensure_collection(namespace):
            logger.error(f"Failed to ensure collection for namespace {namespace}")
            return []
            
        # Get collection name
        collection_name = self.namespace_collections.get(namespace)
        if not collection_name:
            logger.error(f"No collection found for namespace: {namespace}")
            return []
            
        try:
            # Generate embedding for the query
            query_embedding = self.vector_model.encode(query)
            
            # Search based on vector DB type
            if self.vector_db_name == "chromadb":
                # ChromaDB implementation
                collection = self.vector_client.get_collection(name=collection_name)
                
                # Search using the embedding
                search_results = collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=limit * 2  # Request more results to account for filtering
                )
                
                # Format the results
                formatted_results = []
                
                # ChromaDB returns results in a dictionary with lists
                ids = search_results.get('ids', [[]])[0]
                documents = search_results.get('documents', [[]])[0]
                metadatas = search_results.get('metadatas', [[]])[0]
                distances = search_results.get('distances', [[]])[0]
                
                for i in range(len(ids)):
                    # Convert distances to relevance scores (lower distance = higher relevance)
                    # Normalize to 0-1 range where 1 is highest relevance
                    distance = distances[i] if i < len(distances) else 1.0
                    relevance = 1.0 - min(distance, 1.0)  # Cap at 1.0
                    
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    document = documents[i] if i < len(documents) else ""
                    
                    formatted_results.append({
                        "id": ids[i] if i < len(ids) else "",
                        "content": document,
                        "metadata": {
                            "timestamp": metadata.get("timestamp", ""),
                            "client_id": metadata.get("client_id", ""),
                            "namespace": metadata.get("namespace", namespace)
                        },
                        "relevance": relevance
                    })
                    
                return formatted_results[:limit]
                
            elif self.vector_db_name == "qdrant":
                # Qdrant implementation
                try:
                    # Try with standard API
                    search_results = self.vector_client.search(
                        collection_name=collection_name,
                        query_vector=query_embedding.tolist(),
                        limit=limit * 2  # Request more results to account for filtering
                    )
                except TypeError:
                    # Fall back to alternate API
                    search_results = self.vector_client.search(
                        collection_name=collection_name,
                        vector=query_embedding.tolist(),
                        limit=limit * 2
                    )
                
                # Format the results
                formatted_results = []
                for result in search_results:
                    try:
                        # Handle different result formats
                        if hasattr(result, 'payload'):
                            # Standard object format
                            payload = result.payload
                            score = getattr(result, 'score', 1.0)
                        elif isinstance(result, dict):
                            # Dictionary format
                            payload = result.get('payload', {})
                            score = result.get('score', 1.0)
                        else:
                            # Unknown format, try to adapt
                            payload = getattr(result, 'payload', {})
                            if not payload and hasattr(result, '__dict__'):
                                payload = result.__dict__
                            score = 1.0
                                
                        formatted_results.append({
                            "id": payload.get("id", ""),
                            "content": payload.get("content", ""),
                            "metadata": payload.get("metadata", {}),
                            "relevance": score
                        })
                    except Exception as e:
                        logger.warning(f"Error formatting Qdrant result: {e}, skipping")
                        
                return formatted_results[:limit]
                
            elif self.vector_db_name == "faiss":
                # FAISS implementation using the VectorStore
                from engram.core.vector_store import VectorStore
                
                # Ensure we have a VectorStore instance
                if not hasattr(self, '_faiss_store'):
                    # Initialize FAISS store if not already done
                    vector_path = os.path.join(self.vector_db_path, "faiss_vectors")
                    self._faiss_store = VectorStore(
                        data_path=vector_path,
                        dimension=self.embedding_model.get_sentence_embedding_dimension()
                    )
                    # Load existing compartments
                    for comp_file in Path(vector_path).glob("*.index"):
                        compartment_name = comp_file.stem
                        self._faiss_store.load(compartment_name)
                
                # Use namespace as compartment name
                compartment = namespace
                
                # Search in FAISS
                search_results = self._faiss_store.search(
                    compartment=compartment,
                    query=query,
                    top_k=limit
                )
                
                # Format results to match expected format
                formatted_results = []
                for result in search_results:
                    metadata = result.get('metadata', {})
                    formatted_results.append({
                        "id": metadata.get('memory_id', result.get('id', '')),
                        "content": result.get('text', ''),
                        "metadata": metadata,
                        "relevance": result.get('score', 0.0)
                    })
                
                return formatted_results
                
            elif self.vector_db_name == "lancedb":
                # LanceDB implementation
                table = self.vector_client.open_table(collection_name)
                
                # Search using vector similarity
                search_results = table.search(query_embedding.tolist()).limit(limit * 2).to_pandas()
                
                # Format the results
                formatted_results = []
                for idx, row in search_results.iterrows():
                    # Calculate relevance score from distance (assuming cosine similarity)
                    # LanceDB returns results ordered by similarity
                    relevance = 1.0 - (idx / len(search_results))  # Simple ranking-based score
                    
                    # Parse metadata from JSON string
                    metadata = {}
                    try:
                        import json
                        metadata = json.loads(row.get('metadata', '{}'))
                    except:
                        pass
                    
                    formatted_results.append({
                        "id": row.get('id', ''),
                        "content": row.get('content', ''),
                        "metadata": metadata,
                        "relevance": relevance
                    })
                
                return formatted_results[:limit]
                
            else:
                raise ValueError(f"Unknown vector database: {self.vector_db_name}")
                
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
            
    def clear_namespace(self, namespace: str) -> bool:
        """
        Clear all memories in a namespace.
        
        Args:
            namespace: The namespace to clear
            
        Returns:
            Boolean indicating success
        """
        # Get collection name
        collection_name = self.namespace_collections.get(namespace)
        if not collection_name:
            logger.warning(f"No collection found for namespace: {namespace}")
            return False
            
        try:
            if self.vector_db_name == "chromadb":
                # ChromaDB implementation - delete and recreate collection
                self.vector_client.delete_collection(name=collection_name)
                self.vector_client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=None
                )
                
            elif self.vector_db_name == "qdrant":
                # Qdrant implementation
                try:
                    # Try with newer API style first
                    from qdrant_client.http import models
                    self.vector_client.delete(
                        collection_name=collection_name,
                        points_selector=models.Filter()  # Empty filter to match all points
                    )
                except (ImportError, AttributeError):
                    # Fall back to simpler API style
                    self.vector_client.delete(
                        collection_name=collection_name,
                        points_selector={}  # Empty filter to match all points
                    )
                    
            elif self.vector_db_name == "faiss":
                # FAISS implementation using the VectorStore
                from engram.core.vector_store import VectorStore
                
                # Ensure we have a VectorStore instance
                if not hasattr(self, '_faiss_store'):
                    # Initialize FAISS store if not already done
                    vector_path = os.path.join(self.vector_db_path, "faiss_vectors")
                    self._faiss_store = VectorStore(
                        data_path=vector_path,
                        dimension=self.embedding_model.get_sentence_embedding_dimension()
                    )
                
                # Use namespace as compartment name
                compartment = namespace
                
                # Delete the compartment
                self._faiss_store.delete(compartment)
                
                logger.debug(f"Cleared namespace {namespace} in FAISS")
                
            elif self.vector_db_name == "lancedb":
                # LanceDB implementation - drop and recreate table
                try:
                    self.vector_client.drop_table(collection_name)
                    logger.debug(f"Dropped LanceDB table {collection_name}")
                except Exception as e:
                    logger.warning(f"Failed to drop table {collection_name}: {e}")
                
                # Recreate the table with schema
                import pyarrow as pa
                schema = pa.schema([
                    pa.field("id", pa.string()),
                    pa.field("content", pa.string()),
                    pa.field("vector", pa.list_(pa.float32(), self.vector_dim)),
                    pa.field("metadata", pa.string())  # JSON string
                ])
                self.vector_client.create_table(collection_name, schema=schema)
                logger.debug(f"Recreated LanceDB table {collection_name}")
                
            else:
                raise ValueError(f"Unknown vector database: {self.vector_db_name}")
                
            logger.info(f"Cleared namespace {namespace} in vector storage")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing namespace in vector storage: {e}")
            return False