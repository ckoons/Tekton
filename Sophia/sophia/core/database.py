"""
Database layer for Sophia
Provides persistent storage for experiments, metrics, intelligence profiles, and recommendations
"""

import os
import json
import asyncio
import aiosqlite
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SophiaDatabase:
    """
    Database layer for Sophia component
    Handles all persistent storage operations
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            # Default to data directory
            self.db_path = Path(__file__).parent.parent / "data" / "sophia.db"
        else:
            self.db_path = Path(db_path)
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.connection = None
        self.is_initialized = False
        
        logger.info(f"Database path: {self.db_path}")
    
    async def initialize(self) -> bool:
        """
        Initialize database and create tables
        
        Returns:
            True if successful
        """
        try:
            logger.info("Initializing Sophia database...")
            
            # Open connection
            self.connection = await aiosqlite.connect(str(self.db_path))
            self.connection.row_factory = aiosqlite.Row
            
            # Create tables
            await self._create_tables()
            
            # Migrate existing JSON data if present
            await self._migrate_json_data()
            
            self.is_initialized = True
            logger.info("Sophia database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.is_initialized = False
    
    async def _create_tables(self):
        """Create database tables"""
        
        # Experiments table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                experiment_type TEXT NOT NULL,
                target_components TEXT,  -- JSON array
                hypothesis TEXT,
                metrics TEXT,  -- JSON array
                parameters TEXT,  -- JSON object
                status TEXT NOT NULL DEFAULT 'draft',
                start_time TEXT,
                end_time TEXT,
                actual_start_time TEXT,
                actual_end_time TEXT,
                sample_size INTEGER,
                min_confidence REAL,
                tags TEXT,  -- JSON array
                results TEXT,  -- JSON object
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Metrics table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                tags TEXT,  -- JSON object
                context TEXT,  -- JSON object
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_metrics_component (component_name),
                INDEX idx_metrics_name (metric_name),
                INDEX idx_metrics_timestamp (timestamp)
            )
        """)
        
        # Intelligence profiles table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_profiles (
                id TEXT PRIMARY KEY,
                component_name TEXT NOT NULL UNIQUE,
                profile_data TEXT NOT NULL,  -- JSON object
                overall_score REAL,
                dimensions TEXT,  -- JSON object
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                INDEX idx_intelligence_component (component_name)
            )
        """)
        
        # Intelligence measurements table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_name TEXT NOT NULL,
                dimension TEXT NOT NULL,
                value REAL NOT NULL,
                context TEXT,  -- JSON object
                measurement_type TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_intelligence_measurements_component (component_name),
                INDEX idx_intelligence_measurements_dimension (dimension),
                INDEX idx_intelligence_measurements_timestamp (timestamp)
            )
        """)
        
        # Recommendations table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                recommendation_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                target_components TEXT,  -- JSON array
                impact_assessment TEXT,  -- JSON object
                implementation_plan TEXT,  -- JSON object
                rationale TEXT,
                confidence_score REAL,
                tags TEXT,  -- JSON array
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                INDEX idx_recommendations_type (recommendation_type),
                INDEX idx_recommendations_priority (priority),
                INDEX idx_recommendations_status (status)
            )
        """)
        
        # Research projects table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS research_projects (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                research_approach TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'proposed',
                target_components TEXT,  -- JSON array
                methodology TEXT,  -- JSON object
                expected_outcomes TEXT,  -- JSON array
                timeline TEXT,  -- JSON object
                progress TEXT,  -- JSON object
                findings TEXT,  -- JSON object
                tags TEXT,  -- JSON array
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                INDEX idx_research_approach (research_approach),
                INDEX idx_research_status (status)
            )
        """)
        
        # Component registry table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                component_type TEXT NOT NULL,
                status TEXT NOT NULL,
                capabilities TEXT,  -- JSON array
                configuration TEXT,  -- JSON object
                health_status TEXT,  -- JSON object
                last_seen TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                INDEX idx_components_name (name),
                INDEX idx_components_type (component_type),
                INDEX idx_components_status (status)
            )
        """)
        
        await self.connection.commit()
        logger.info("Database tables created successfully")
    
    async def _migrate_json_data(self):
        """Migrate existing JSON data to database"""
        try:
            # Migrate experiments
            experiments_file = self.db_path.parent / "experiments" / "experiments.json"
            if experiments_file.exists():
                with open(experiments_file, 'r') as f:
                    experiments_data = json.load(f)
                
                for exp_id, exp_data in experiments_data.items():
                    await self.save_experiment(exp_data)
                
                logger.info(f"Migrated {len(experiments_data)} experiments from JSON")
            
            # Migrate intelligence profiles
            profiles_file = self.db_path.parent / "intelligence" / "profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r') as f:
                    profiles_data = json.load(f)
                
                for component_name, profile_data in profiles_data.items():
                    await self.save_intelligence_profile(component_name, profile_data)
                
                logger.info(f"Migrated {len(profiles_data)} intelligence profiles from JSON")
                
        except Exception as e:
            logger.warning(f"Error during JSON migration: {str(e)}")
    
    # Experiment operations
    async def save_experiment(self, experiment_data: Dict[str, Any]) -> bool:
        """Save experiment to database"""
        try:
            await self.connection.execute("""
                INSERT OR REPLACE INTO experiments 
                (id, name, description, experiment_type, target_components, hypothesis, 
                 metrics, parameters, status, start_time, end_time, actual_start_time, 
                 actual_end_time, sample_size, min_confidence, tags, results, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                experiment_data.get('id'),
                experiment_data.get('name'),
                experiment_data.get('description'),
                experiment_data.get('experiment_type'),
                json.dumps(experiment_data.get('target_components', [])),
                experiment_data.get('hypothesis'),
                json.dumps(experiment_data.get('metrics', [])),
                json.dumps(experiment_data.get('parameters', {})),
                experiment_data.get('status'),
                experiment_data.get('start_time'),
                experiment_data.get('end_time'),
                experiment_data.get('actual_start_time'),
                experiment_data.get('actual_end_time'),
                experiment_data.get('sample_size'),
                experiment_data.get('min_confidence'),
                json.dumps(experiment_data.get('tags', [])),
                json.dumps(experiment_data.get('results')),
                experiment_data.get('created_at'),
                experiment_data.get('updated_at')
            ))
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving experiment: {str(e)}")
            return False
    
    async def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment by ID"""
        try:
            cursor = await self.connection.execute(
                "SELECT * FROM experiments WHERE id = ?", (experiment_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return self._row_to_experiment(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting experiment: {str(e)}")
            return None
    
    async def query_experiments(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query experiments with optional filters"""
        try:
            query = "SELECT * FROM experiments"
            params = []
            conditions = []
            
            if filters:
                if 'status' in filters and filters['status']:
                    conditions.append("status = ?")
                    params.append(filters['status'])
                
                if 'experiment_type' in filters and filters['experiment_type']:
                    conditions.append("experiment_type = ?")
                    params.append(filters['experiment_type'])
                
                if 'start_after' in filters and filters['start_after']:
                    conditions.append("start_time >= ?")
                    params.append(filters['start_after'])
                
                if 'start_before' in filters and filters['start_before']:
                    conditions.append("start_time <= ?")
                    params.append(filters['start_before'])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC"
            
            if 'limit' in filters:
                query += f" LIMIT {filters['limit']}"
                if 'offset' in filters:
                    query += f" OFFSET {filters['offset']}"
            
            cursor = await self.connection.execute(query, params)
            rows = await cursor.fetchall()
            
            return [self._row_to_experiment(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error querying experiments: {str(e)}")
            return []
    
    async def delete_experiment(self, experiment_id: str) -> bool:
        """Delete experiment"""
        try:
            await self.connection.execute(
                "DELETE FROM experiments WHERE id = ?", (experiment_id,)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting experiment: {str(e)}")
            return False
    
    # Metrics operations
    async def save_metric(self, component_name: str, metric_name: str, value: float,
                         unit: str = None, tags: Dict[str, Any] = None,
                         context: Dict[str, Any] = None, timestamp: str = None) -> bool:
        """Save metric to database"""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow().isoformat() + "Z"
            
            await self.connection.execute("""
                INSERT INTO metrics 
                (component_name, metric_name, value, unit, tags, context, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                component_name,
                metric_name,
                value,
                unit,
                json.dumps(tags) if tags else None,
                json.dumps(context) if context else None,
                timestamp
            ))
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving metric: {str(e)}")
            return False
    
    async def query_metrics(self, component_name: str = None, metric_name: str = None,
                           start_time: str = None, end_time: str = None,
                           limit: int = 1000) -> List[Dict[str, Any]]:
        """Query metrics with filters"""
        try:
            query = "SELECT * FROM metrics"
            params = []
            conditions = []
            
            if component_name:
                conditions.append("component_name = ?")
                params.append(component_name)
            
            if metric_name:
                conditions.append("metric_name = ?")
                params.append(metric_name)
            
            if start_time:
                conditions.append("timestamp >= ?")
                params.append(start_time)
            
            if end_time:
                conditions.append("timestamp <= ?")
                params.append(end_time)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await self.connection.execute(query, params)
            rows = await cursor.fetchall()
            
            return [self._row_to_metric(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error querying metrics: {str(e)}")
            return []
    
    # Intelligence profile operations
    async def save_intelligence_profile(self, component_name: str, 
                                      profile_data: Dict[str, Any]) -> bool:
        """Save intelligence profile"""
        try:
            now = datetime.utcnow().isoformat() + "Z"
            profile_id = f"profile_{component_name}"
            
            await self.connection.execute("""
                INSERT OR REPLACE INTO intelligence_profiles 
                (id, component_name, profile_data, overall_score, dimensions, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                component_name,
                json.dumps(profile_data),
                profile_data.get('overall_score'),
                json.dumps(profile_data.get('dimensions', {})),
                profile_data.get('created_at', now),
                now
            ))
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving intelligence profile: {str(e)}")
            return False
    
    async def get_intelligence_profile(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get intelligence profile for component"""
        try:
            cursor = await self.connection.execute(
                "SELECT * FROM intelligence_profiles WHERE component_name = ?", 
                (component_name,)
            )
            row = await cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'component_name': row['component_name'],
                    'profile_data': json.loads(row['profile_data']),
                    'overall_score': row['overall_score'],
                    'dimensions': json.loads(row['dimensions']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting intelligence profile: {str(e)}")
            return None
    
    # Helper methods
    def _row_to_experiment(self, row) -> Dict[str, Any]:
        """Convert database row to experiment dict"""
        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'experiment_type': row['experiment_type'],
            'target_components': json.loads(row['target_components']) if row['target_components'] else [],
            'hypothesis': row['hypothesis'],
            'metrics': json.loads(row['metrics']) if row['metrics'] else [],
            'parameters': json.loads(row['parameters']) if row['parameters'] else {},
            'status': row['status'],
            'start_time': row['start_time'],
            'end_time': row['end_time'],
            'actual_start_time': row['actual_start_time'],
            'actual_end_time': row['actual_end_time'],
            'sample_size': row['sample_size'],
            'min_confidence': row['min_confidence'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'results': json.loads(row['results']) if row['results'] else None,
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    def _row_to_metric(self, row) -> Dict[str, Any]:
        """Convert database row to metric dict"""
        return {
            'id': row['id'],
            'component_name': row['component_name'],
            'metric_name': row['metric_name'],
            'value': row['value'],
            'unit': row['unit'],
            'tags': json.loads(row['tags']) if row['tags'] else {},
            'context': json.loads(row['context']) if row['context'] else {},
            'timestamp': row['timestamp'],
            'created_at': row['created_at']
        }


# Global database instance
_database = None

async def get_database() -> SophiaDatabase:
    """Get global database instance"""
    global _database
    if _database is None:
        _database = SophiaDatabase()
        await _database.initialize()
    return _database

async def close_database():
    """Close global database instance"""
    global _database
    if _database:
        await _database.close()
        _database = None