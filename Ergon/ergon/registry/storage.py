"""
Registry Storage Layer for Ergon Container Management.

Provides SQLite-based storage for deployable units with JSON schema support,
lineage tracking, and standards compliance checking.

Casey Method principles: simple, works, hard to screw up.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        state_checkpoint,
        performance_boundary,
        danger_zone
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Registry Storage Architecture",
    description="SQLite-based JSON storage with singleton pattern for deployable units",
    rationale="SQLite provides ACID compliance, zero configuration, and embedded operation. Singleton pattern prevents connection conflicts and ensures consistent state.",
    alternatives_considered=["PostgreSQL (overkill)", "File-based JSON (no ACID)", "In-memory (no persistence)"],
    impacts=["registry_performance", "data_consistency", "deployment_simplicity"],
    decided_by="Casey, Ani, Amy",
    decision_date="2025-08-22"
)
@state_checkpoint(
    title="Registry Persistent Storage",
    description="SQLite database storing all deployable units with JSON content",
    state_type="persistent",
    persistence=True,
    consistency_requirements="ACID transactions, foreign key constraints for lineage",
    recovery_strategy="Database file backup, transaction rollback on errors"
)
class RegistryStorage:
    """SQLite storage backend for the Ergon Registry."""
    
    def __init__(self, db_path: str = "ergon_registry.db"):
        """
        Initialize the registry storage.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables and indexes if they don't exist."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        
        cursor = self.connection.cursor()
        
        # Create main registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registry (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                version TEXT NOT NULL,
                name TEXT NOT NULL,
                created TEXT NOT NULL,
                updated TEXT NOT NULL,
                meets_standards INTEGER DEFAULT 0,
                lineage TEXT,  -- JSON array of parent IDs
                source TEXT,    -- JSON object with project info
                content TEXT NOT NULL,  -- JSON content
                metadata TEXT   -- Additional metadata as JSON
            )
        """)
        
        # Create indexes for efficient searching
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_registry_type 
            ON registry(type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_registry_name 
            ON registry(name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_registry_standards 
            ON registry(meets_standards)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_registry_created 
            ON registry(created)
        """)
        
        self.connection.commit()
        logger.info(f"Registry database initialized at {self.db_path}")
    
    def store(self, json_object: Dict[str, Any]) -> str:
        """
        Store a JSON object in the registry.
        
        Args:
            json_object: The deployable unit to store
            
        Returns:
            The ID of the stored object
        """
        # Generate ID if not provided
        if 'id' not in json_object:
            json_object['id'] = str(uuid.uuid4())
        
        # Set timestamps
        now = datetime.utcnow().isoformat()
        if 'created' not in json_object:
            json_object['created'] = now
        json_object['updated'] = now
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO registry 
                (id, type, version, name, created, updated, meets_standards, 
                 lineage, source, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                json_object['id'],
                json_object.get('type', 'solution'),
                json_object.get('version', '1.0.0'),
                json_object.get('name', 'Unnamed'),
                json_object['created'],
                json_object['updated'],
                1 if json_object.get('meets_standards', False) else 0,
                json.dumps(json_object.get('lineage', [])),
                json.dumps(json_object.get('source', {})),
                json.dumps(json_object.get('content', {})),
                json.dumps(json_object.get('metadata', {}))
            ))
            
            self.connection.commit()
            logger.info(f"Stored registry entry: {json_object['id']}")
            return json_object['id']
            
        except Exception as e:
            logger.error(f"Failed to store registry entry: {e}")
            self.connection.rollback()
            raise
    
    def retrieve(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a JSON object by ID.
        
        Args:
            entry_id: The ID of the object to retrieve
            
        Returns:
            The JSON object if found, None otherwise
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM registry WHERE id = ?
        """, (entry_id,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
    
    def search(self, 
               type: Optional[str] = None,
               name: Optional[str] = None,
               meets_standards: Optional[bool] = None,
               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for registry entries with filters.
        
        Args:
            type: Filter by type
            name: Filter by name (supports partial match)
            meets_standards: Filter by standards compliance
            limit: Maximum number of results
            
        Returns:
            List of matching JSON objects
        """
        query = "SELECT * FROM registry WHERE 1=1"
        params = []
        
        if type:
            query += " AND type = ?"
            params.append(type)
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if meets_standards is not None:
            query += " AND meets_standards = ?"
            params.append(1 if meets_standards else 0)
        
        query += " ORDER BY created DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append(self._row_to_dict(row))
        
        return results
    
    def list_types(self) -> List[str]:
        """
        Get all unique types in the registry.
        
        Returns:
            List of unique type values
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT type FROM registry ORDER BY type")
        return [row[0] for row in cursor.fetchall()]
    
    @danger_zone(
        title="Registry Entry Deletion with Safeguards",
        description="Deletes registry entries while preventing orphaned dependencies",
        risk_level="medium",
        risks=["orphaned dependencies", "broken lineage chains", "data loss"],
        mitigation="Pre-deletion dependency check, transaction rollback on error",
        review_required=False
    )
    def delete(self, entry_id: str) -> bool:
        """
        Delete a registry entry (with safeguards).
        
        Args:
            entry_id: The ID of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        cursor = self.connection.cursor()
        
        # Check if entry exists and has no dependents
        cursor.execute("""
            SELECT lineage FROM registry WHERE lineage LIKE ?
        """, (f'%"{entry_id}"%',))
        
        dependents = cursor.fetchall()
        if dependents:
            logger.warning(f"Cannot delete {entry_id}: has {len(dependents)} dependents")
            raise ValueError(f"Cannot delete entry with dependents")
        
        cursor.execute("DELETE FROM registry WHERE id = ?", (entry_id,))
        deleted = cursor.rowcount > 0
        
        if deleted:
            self.connection.commit()
            logger.info(f"Deleted registry entry: {entry_id}")
        
        return deleted
    
    def check_standards(self, entry_id: str) -> Dict[str, Any]:
        """
        Check if an entry meets Tekton standards.
        
        Args:
            entry_id: The ID of the entry to check
            
        Returns:
            Compliance report with details
        """
        entry = self.retrieve(entry_id)
        if not entry:
            return {"error": "Entry not found"}
        
        # TODO: Implement actual standards checking logic
        # This will integrate with the Tekton Standards document
        report = {
            "id": entry_id,
            "name": entry.get("name"),
            "type": entry.get("type"),
            "meets_standards": entry.get("meets_standards", False),
            "checks": {
                "has_documentation": bool(entry.get("content", {}).get("documentation")),
                "has_tests": bool(entry.get("content", {}).get("tests")),
                "has_version": bool(entry.get("version")),
                "has_source": bool(entry.get("source")),
            }
        }
        
        # Calculate overall compliance
        report["compliance_score"] = sum(report["checks"].values()) / len(report["checks"])
        
        return report
    
    def get_lineage(self, entry_id: str) -> List[Dict[str, Any]]:
        """
        Get the lineage (history) of a solution.
        
        Args:
            entry_id: The ID of the entry
            
        Returns:
            List of ancestor entries, newest to oldest
        """
        entry = self.retrieve(entry_id)
        if not entry:
            return []
        
        lineage = []
        parent_ids = entry.get("lineage", [])
        
        for parent_id in parent_ids:
            parent = self.retrieve(parent_id)
            if parent:
                lineage.append(parent)
        
        return lineage
    
    def update_standards_compliance(self, entry_id: str, meets_standards: bool) -> bool:
        """
        Update the standards compliance status of an entry.
        
        Args:
            entry_id: The ID of the entry
            meets_standards: Whether the entry meets standards
            
        Returns:
            True if updated, False if not found
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE registry 
            SET meets_standards = ?, updated = ?
            WHERE id = ?
        """, (1 if meets_standards else 0, datetime.utcnow().isoformat(), entry_id))
        
        updated = cursor.rowcount > 0
        if updated:
            self.connection.commit()
            logger.info(f"Updated standards compliance for {entry_id}: {meets_standards}")
        
        return updated
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary."""
        return {
            "id": row["id"],
            "type": row["type"],
            "version": row["version"],
            "name": row["name"],
            "created": row["created"],
            "updated": row["updated"],
            "meets_standards": bool(row["meets_standards"]),
            "lineage": json.loads(row["lineage"]) if row["lineage"] else [],
            "source": json.loads(row["source"]) if row["source"] else {},
            "content": json.loads(row["content"]) if row["content"] else {},
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
        }
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Registry database connection closed")