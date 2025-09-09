"""
TinyDB Document Adapter - Implementation for document database using TinyDB.

This module provides a concrete implementation of the DocumentDatabaseAdapter
interface using TinyDB for lightweight, file-based document storage.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from tinydb import TinyDB, Query, where
    from tinydb.storages import JSONStorage
    from tinydb.middlewares import CachingMiddleware
    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False
    # Fallback to simple JSON file storage
    
from hermes.core.database.adapters.document import DocumentDatabaseAdapter

logger = logging.getLogger("hermes.database.document")


class JSONDocumentStore:
    """Simple JSON-based document store as fallback."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.documents = {}
        self.load()
    
    def load(self):
        """Load documents from file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self.documents = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load documents: {e}")
                self.documents = {}
    
    def save(self):
        """Save documents to file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.documents, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save documents: {e}")
    
    def insert(self, doc: Dict[str, Any]) -> str:
        """Insert a document."""
        doc_id = doc.get('_id', str(datetime.now().timestamp()))
        self.documents[doc_id] = doc
        self.save()
        return doc_id
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find documents matching query."""
        results = []
        for doc_id, doc in self.documents.items():
            if self._matches(doc, query):
                results.append(doc)
        return results
    
    def update(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document."""
        if doc_id in self.documents:
            self.documents[doc_id].update(updates)
            self.save()
            return True
        return False
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self.save()
            return True
        return False
    
    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query."""
        for key, value in query.items():
            if key not in doc or doc[key] != value:
                return False
        return True


class TinyDBDocumentAdapter(DocumentDatabaseAdapter):
    """
    Document adapter using TinyDB for lightweight document storage.
    
    Provides flexible schema-less document storage with query capabilities,
    using TinyDB for simplicity or falling back to JSON files.
    """
    
    def __init__(self, namespace: str = "default", config: Optional[Dict[str, Any]] = None):
        """
        Initialize document adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration (db_path, etc.)
        """
        self.namespace = namespace
        self.config = config or {}
        
        # Set database path
        base_path = Path(self.config.get('db_path', '/tmp/tekton/hermes/documents'))
        base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = base_path / f"{namespace}.json"
        
        self.db = None
        self.executor = ThreadPoolExecutor(max_workers=1)  # For async operations
        
        # Stats tracking
        self.stats = {
            'inserts': 0,
            'finds': 0,
            'updates': 0,
            'deletes': 0,
            'backend': 'tinydb' if TINYDB_AVAILABLE else 'json'
        }
        
        logger.info(f"Document adapter initialized for namespace '{namespace}' at {self.db_path}")
    
    async def connect(self) -> bool:
        """
        Connect to document database.
        
        Returns:
            True if connection successful
        """
        try:
            if TINYDB_AVAILABLE:
                # Use TinyDB with caching middleware for better performance
                self.db = TinyDB(
                    self.db_path,
                    storage=CachingMiddleware(JSONStorage)
                )
                logger.info(f"Connected to TinyDB at {self.db_path}")
            else:
                # Fallback to simple JSON storage
                self.db = JSONDocumentStore(self.db_path)
                logger.info(f"Using JSON document store at {self.db_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to document database: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from document database.
        
        Returns:
            True if disconnection successful
        """
        try:
            if TINYDB_AVAILABLE and self.db:
                self.db.close()
            self.db = None
            self.executor.shutdown(wait=False)
            logger.info("Disconnected from document database")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return False
    
    async def insert(self, document: Dict[str, Any]) -> str:
        """
        Insert a document.
        
        Args:
            document: Document to insert
            
        Returns:
            Document ID of inserted document
        """
        if not self.db:
            await self.connect()
        
        self.stats['inserts'] += 1
        
        # Add metadata
        document['_namespace'] = self.namespace
        document['_created_at'] = datetime.now().isoformat()
        document['_updated_at'] = datetime.now().isoformat()
        
        # Run in executor for async operation
        def _insert():
            if TINYDB_AVAILABLE:
                doc_id = self.db.insert(document)
                return str(doc_id)
            else:
                return self.db.insert(document)
        
        doc_id = await asyncio.get_event_loop().run_in_executor(
            self.executor, _insert
        )
        
        logger.debug(f"Inserted document with ID: {doc_id}")
        return doc_id
    
    async def find(self, 
                  query: Dict[str, Any],
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find documents matching a query.
        
        Args:
            query: Query conditions
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        if not self.db:
            await self.connect()
        
        self.stats['finds'] += 1
        
        # Add namespace to query
        query['_namespace'] = self.namespace
        
        # Run in executor for async operation
        def _find():
            if TINYDB_AVAILABLE:
                # Build TinyDB query
                q = Query()
                conditions = []
                for key, value in query.items():
                    if isinstance(value, dict):
                        # Handle operators like {'$gt': 5}
                        for op, val in value.items():
                            if op == '$gt':
                                conditions.append(q[key] > val)
                            elif op == '$gte':
                                conditions.append(q[key] >= val)
                            elif op == '$lt':
                                conditions.append(q[key] < val)
                            elif op == '$lte':
                                conditions.append(q[key] <= val)
                            elif op == '$ne':
                                conditions.append(q[key] != val)
                            elif op == '$in':
                                conditions.append(q[key].test(lambda x: x in val))
                            elif op == '$regex':
                                import re
                                conditions.append(q[key].test(lambda x: re.match(val, x)))
                    else:
                        conditions.append(q[key] == value)
                
                # Combine conditions with AND
                if conditions:
                    combined = conditions[0]
                    for cond in conditions[1:]:
                        combined = combined & cond
                    results = self.db.search(combined)
                else:
                    results = self.db.all()
                
                if limit:
                    results = results[:limit]
                return results
            else:
                results = self.db.find(query)
                if limit:
                    results = results[:limit]
                return results
        
        results = await asyncio.get_event_loop().run_in_executor(
            self.executor, _find
        )
        
        logger.debug(f"Found {len(results)} documents")
        return results
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching a query.
        
        Args:
            query: Query conditions
            
        Returns:
            Matching document or None
        """
        results = await self.find(query, limit=1)
        return results[0] if results else None
    
    async def update(self,
                    query: Dict[str, Any],
                    updates: Dict[str, Any]) -> int:
        """
        Update documents matching a query.
        
        Args:
            query: Query to match documents
            updates: Updates to apply
            
        Returns:
            Number of documents updated
        """
        if not self.db:
            await self.connect()
        
        self.stats['updates'] += 1
        
        # Add namespace to query
        query['_namespace'] = self.namespace
        
        # Update metadata
        updates['_updated_at'] = datetime.now().isoformat()
        
        # Run in executor for async operation
        def _update():
            if TINYDB_AVAILABLE:
                # Build TinyDB query (similar to find)
                q = Query()
                conditions = []
                for key, value in query.items():
                    conditions.append(q[key] == value)
                
                if conditions:
                    combined = conditions[0]
                    for cond in conditions[1:]:
                        combined = combined & cond
                    
                    # Update documents
                    doc_ids = self.db.update(updates, combined)
                    return len(doc_ids) if isinstance(doc_ids, list) else 1
                return 0
            else:
                # For JSON store, find and update
                docs = self.db.find(query)
                count = 0
                for doc in docs:
                    if '_id' in doc:
                        self.db.update(doc['_id'], updates)
                        count += 1
                return count
        
        count = await asyncio.get_event_loop().run_in_executor(
            self.executor, _update
        )
        
        logger.debug(f"Updated {count} documents")
        return count
    
    async def delete(self, query: Dict[str, Any]) -> int:
        """
        Delete documents matching a query.
        
        Args:
            query: Query to match documents for deletion
            
        Returns:
            Number of documents deleted
        """
        if not self.db:
            await self.connect()
        
        self.stats['deletes'] += 1
        
        # Add namespace to query
        query['_namespace'] = self.namespace
        
        # Run in executor for async operation
        def _delete():
            if TINYDB_AVAILABLE:
                # Build TinyDB query
                q = Query()
                conditions = []
                for key, value in query.items():
                    conditions.append(q[key] == value)
                
                if conditions:
                    combined = conditions[0]
                    for cond in conditions[1:]:
                        combined = combined & cond
                    
                    # Delete documents
                    doc_ids = self.db.remove(combined)
                    return len(doc_ids) if isinstance(doc_ids, list) else 0
                return 0
            else:
                # For JSON store, find and delete
                docs = self.db.find(query)
                count = 0
                for doc in docs:
                    if '_id' in doc:
                        self.db.delete(doc['_id'])
                        count += 1
                return count
        
        count = await asyncio.get_event_loop().run_in_executor(
            self.executor, _delete
        )
        
        logger.debug(f"Deleted {count} documents")
        return count
    
    async def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents matching a query.
        
        Args:
            query: Optional query conditions
            
        Returns:
            Number of matching documents
        """
        if not self.db:
            await self.connect()
        
        if query:
            docs = await self.find(query)
            return len(docs)
        else:
            # Count all in namespace
            docs = await self.find({'_namespace': self.namespace})
            return len(docs)
    
    # Additional utility methods
    
    async def create_index(self, field: str) -> bool:
        """
        Create an index on a field (no-op for TinyDB, but kept for interface).
        
        Args:
            field: Field to index
            
        Returns:
            True (TinyDB doesn't have explicit indexes)
        """
        logger.debug(f"Index creation requested for field '{field}' (no-op for TinyDB)")
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary of stats
        """
        stats = self.stats.copy()
        
        # Add document count
        stats['document_count'] = await self.count()
        
        # Add file size
        if self.db_path.exists():
            stats['file_size_bytes'] = self.db_path.stat().st_size
            stats['file_size_mb'] = stats['file_size_bytes'] / (1024 * 1024)
        
        return stats
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform aggregation operations (simplified for TinyDB).
        
        Args:
            pipeline: Aggregation pipeline
            
        Returns:
            Aggregation results
        """
        # Simplified aggregation - just support basic operations
        results = await self.find({'_namespace': self.namespace})
        
        for stage in pipeline:
            if '$match' in stage:
                # Filter results
                query = stage['$match']
                results = [doc for doc in results if self._matches_query(doc, query)]
            
            elif '$sort' in stage:
                # Sort results
                sort_spec = stage['$sort']
                for field, direction in sort_spec.items():
                    results = sorted(results, key=lambda x: x.get(field, ''), 
                                   reverse=(direction == -1))
            
            elif '$limit' in stage:
                # Limit results
                limit = stage['$limit']
                results = results[:limit]
            
            elif '$project' in stage:
                # Project fields
                projection = stage['$project']
                new_results = []
                for doc in results:
                    new_doc = {}
                    for field, include in projection.items():
                        if include and field in doc:
                            new_doc[field] = doc[field]
                    new_results.append(new_doc)
                results = new_results
        
        return results
    
    def _matches_query(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query."""
        for key, value in query.items():
            if isinstance(value, dict):
                # Handle operators
                for op, val in value.items():
                    doc_val = doc.get(key)
                    if op == '$gt' and not (doc_val and doc_val > val):
                        return False
                    elif op == '$gte' and not (doc_val and doc_val >= val):
                        return False
                    elif op == '$lt' and not (doc_val and doc_val < val):
                        return False
                    elif op == '$lte' and not (doc_val and doc_val <= val):
                        return False
                    elif op == '$ne' and doc_val == val:
                        return False
                    elif op == '$in' and doc_val not in val:
                        return False
            else:
                if key not in doc or doc[key] != value:
                    return False
        return True