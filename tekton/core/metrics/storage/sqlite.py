"""
SQLite storage for metrics data.

This module provides SQLite-based storage for metrics data.
"""

import os
import json
import time
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import MetricsStorage
from .schema import SQLITE_SCHEMA, SQLITE_INDEXES

logger = logging.getLogger(__name__)

class SQLiteMetricsStorage(MetricsStorage):
    """Stores metrics in a SQLite database."""
    
    def __init__(self, db_path="metrics.db"):
        """Initialize SQLite storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        for table_name, create_sql in SQLITE_SCHEMA.items():
            cursor.execute(create_sql)
        
        # Create indexes
        for index_sql in SQLITE_INDEXES:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
    
    def store_session(self, session_data):
        """Store a session's metrics data."""
        # Convert to dict if it's a SessionData object
        data = session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Store main session data
            cursor.execute(
                'INSERT INTO sessions (id, prompt, config, start_time, end_time, '
                'response, performance, spectral_metrics, catastrophe_metrics, created_at) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    data['id'],
                    data['prompt'],
                    json.dumps(data['config']),
                    data['start_time'],
                    data.get('end_time'),
                    data.get('response'),
                    json.dumps(data.get('performance', {})),
                    json.dumps(data.get('spectral_metrics', {})),
                    json.dumps(data.get('catastrophe_metrics', {})),
                    time.time()
                )
            )
            
            # Store component activations
            for component_id, activations in data.get('component_activations', {}).items():
                for activation in activations:
                    cursor.execute(
                        'INSERT INTO component_activations (session_id, component_id, '
                        'activation_data, timestamp) VALUES (?, ?, ?, ?)',
                        (
                            data['id'],
                            component_id,
                            json.dumps(activation),
                            activation.get('timestamp', 0)
                        )
                    )
            
            # Store propagation steps
            for step in data.get('propagation_path', []):
                cursor.execute(
                    'INSERT INTO propagation_steps (session_id, source, destination, '
                    'info_content, data, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                    (
                        data['id'],
                        step['source'],
                        step['destination'],
                        step.get('info_content', 0),
                        json.dumps({k: v for k, v in step.items() 
                                 if k not in ['source', 'destination', 'info_content', 'timestamp']}),
                        step.get('timestamp', 0)
                    )
                )
            
            # Store parameter usage
            for component_id, usage in data.get('parameter_usage', {}).items():
                cursor.execute(
                    'INSERT INTO parameter_usage (session_id, component_id, total_params, '
                    'active_params, utilization, layer_data, timestamp) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (
                        data['id'],
                        component_id,
                        usage.get('total', 0),
                        usage.get('active', 0),
                        usage.get('utilization', 0),
                        json.dumps(usage.get('layers', {})),
                        usage.get('timestamp', 0)
                    )
                )
                
            # Store latent reasoning records
            for record in data.get('latent_reasoning', []):
                cursor.execute(
                    'INSERT INTO latent_reasoning (session_id, component_id, iteration, '
                    'initial_confidence, final_confidence, iterations_required, '
                    'cognitive_convergence_rate, reasoning_data, timestamp) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        data['id'],
                        record.get('component_id', ''),
                        record.get('iteration', 0),
                        record.get('initial_confidence', 0.0),
                        record.get('final_confidence', 0.0),
                        record.get('iterations_required', 0),
                        record.get('cognitive_convergence_rate', 0.0),
                        json.dumps({k: v for k, v in record.items() 
                                 if k not in ['component_id', 'iteration', 'initial_confidence', 
                                             'final_confidence', 'iterations_required', 
                                             'cognitive_convergence_rate', 'timestamp']}),
                        record.get('timestamp', 0)
                    )
                )
                
            # Store cross-modal operations
            for operation in data.get('cross_modal_operations', []):
                cursor.execute(
                    'INSERT INTO cross_modal_operations (session_id, source_modality, '
                    'target_modality, operation_type, success, operation_data, timestamp) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (
                        data['id'],
                        operation.get('source_modality', ''),
                        operation.get('target_modality', ''),
                        operation.get('operation_type', ''),
                        1 if operation.get('success', False) else 0,
                        json.dumps({k: v for k, v in operation.items() 
                                 if k not in ['source_modality', 'target_modality', 
                                             'operation_type', 'success', 'timestamp']}),
                        operation.get('timestamp', 0)
                    )
                )
                
            # Store concept stability data
            for concept_id, observations in data.get('concept_stability', {}).items():
                for obs in observations:
                    cursor.execute(
                        'INSERT INTO concept_stability (session_id, concept_id, context, '
                        'vector_representation, stability_data, timestamp) '
                        'VALUES (?, ?, ?, ?, ?, ?)',
                        (
                            data['id'],
                            concept_id,
                            obs.get('context', ''),
                            json.dumps(obs.get('vector_representation', [])),
                            json.dumps({k: v for k, v in obs.items() 
                                     if k not in ['context', 'vector_representation', 'timestamp']}),
                            obs.get('timestamp', 0)
                        )
                    )
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing session data: {str(e)}")
            raise
        finally:
            conn.close()
    
    def get_session(self, session_id):
        """Retrieve a session by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get main session data
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
                
            session_data = dict(session_row)
            
            # Parse JSON fields
            for field in ['config', 'performance', 'spectral_metrics', 'catastrophe_metrics']:
                if session_data.get(field):
                    session_data[field] = json.loads(session_data[field])
            
            # Get component activations
            cursor.execute(
                'SELECT component_id, activation_data, timestamp FROM component_activations '
                'WHERE session_id = ? ORDER BY timestamp', (session_id,)
            )
            
            activations = {}
            for row in cursor.fetchall():
                component_id = row['component_id']
                if component_id not in activations:
                    activations[component_id] = []
                
                activation_data = json.loads(row['activation_data'])
                activation_data['timestamp'] = row['timestamp']
                activations[component_id].append(activation_data)
            
            session_data['component_activations'] = activations
            
            # Get propagation steps
            cursor.execute(
                'SELECT source, destination, info_content, data, timestamp FROM propagation_steps '
                'WHERE session_id = ? ORDER BY timestamp', (session_id,)
            )
            
            propagation_path = []
            for row in cursor.fetchall():
                step = {
                    'source': row['source'],
                    'destination': row['destination'],
                    'info_content': row['info_content'],
                    'timestamp': row['timestamp']
                }
                
                # Add additional data if present
                step.update(json.loads(row['data']))
                propagation_path.append(step)
            
            session_data['propagation_path'] = propagation_path
            
            # Get parameter usage
            cursor.execute(
                'SELECT component_id, total_params, active_params, utilization, layer_data, timestamp '
                'FROM parameter_usage WHERE session_id = ?', (session_id,)
            )
            
            parameter_usage = {}
            for row in cursor.fetchall():
                parameter_usage[row['component_id']] = {
                    'total': row['total_params'],
                    'active': row['active_params'],
                    'utilization': row['utilization'],
                    'timestamp': row['timestamp'],
                    'layers': json.loads(row['layer_data'])
                }
            
            session_data['parameter_usage'] = parameter_usage
            
            # Get latent reasoning data
            cursor.execute(
                'SELECT component_id, iteration, initial_confidence, final_confidence, '
                'iterations_required, cognitive_convergence_rate, reasoning_data, timestamp '
                'FROM latent_reasoning WHERE session_id = ? ORDER BY timestamp', (session_id,)
            )
            
            latent_reasoning = []
            for row in cursor.fetchall():
                record = {
                    'component_id': row['component_id'],
                    'iteration': row['iteration'],
                    'initial_confidence': row['initial_confidence'],
                    'final_confidence': row['final_confidence'],
                    'iterations_required': row['iterations_required'],
                    'cognitive_convergence_rate': row['cognitive_convergence_rate'],
                    'timestamp': row['timestamp']
                }
                
                # Add additional data if present
                record.update(json.loads(row['reasoning_data']))
                latent_reasoning.append(record)
            
            session_data['latent_reasoning'] = latent_reasoning
            
            # Get cross-modal operations
            cursor.execute(
                'SELECT source_modality, target_modality, operation_type, success, '
                'operation_data, timestamp FROM cross_modal_operations '
                'WHERE session_id = ? ORDER BY timestamp', (session_id,)
            )
            
            cross_modal_operations = []
            for row in cursor.fetchall():
                operation = {
                    'source_modality': row['source_modality'],
                    'target_modality': row['target_modality'],
                    'operation_type': row['operation_type'],
                    'success': bool(row['success']),
                    'timestamp': row['timestamp']
                }
                
                # Add additional data if present
                operation.update(json.loads(row['operation_data']))
                cross_modal_operations.append(operation)
            
            session_data['cross_modal_operations'] = cross_modal_operations
            
            # Get concept stability data
            cursor.execute(
                'SELECT concept_id, context, vector_representation, stability_data, timestamp '
                'FROM concept_stability WHERE session_id = ? ORDER BY timestamp', (session_id,)
            )
            
            concept_stability = {}
            for row in cursor.fetchall():
                concept_id = row['concept_id']
                
                if concept_id not in concept_stability:
                    concept_stability[concept_id] = []
                
                observation = {
                    'context': row['context'],
                    'vector_representation': json.loads(row['vector_representation']),
                    'timestamp': row['timestamp']
                }
                
                # Add additional data if present
                observation.update(json.loads(row['stability_data']))
                concept_stability[concept_id].append(observation)
            
            session_data['concept_stability'] = concept_stability
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error retrieving session data: {str(e)}")
            raise
        finally:
            conn.close()
    
    def get_sessions(self, filters=None, limit=100, offset=0):
        """Retrieve multiple sessions with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Build query based on filters
            query = "SELECT id FROM sessions"
            params = []
            
            if filters:
                conditions = []
                
                if 'start_time_min' in filters:
                    conditions.append("start_time >= ?")
                    params.append(filters['start_time_min'])
                
                if 'start_time_max' in filters:
                    conditions.append("start_time <= ?")
                    params.append(filters['start_time_max'])
                
                if 'prompt_like' in filters:
                    conditions.append("prompt LIKE ?")
                    params.append(f"%{filters['prompt_like']}%")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            session_ids = [row['id'] for row in cursor.fetchall()]
            
            # Get full data for each session
            sessions = []
            for session_id in session_ids:
                session_data = self.get_session(session_id)
                if session_data:
                    sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving sessions: {str(e)}")
            raise
        finally:
            conn.close()
            
    def get_spectral_metrics(self, filters=None, limit=100):
        """Get spectral metrics for multiple sessions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Build query based on filters
            query = "SELECT id, start_time, spectral_metrics, catastrophe_metrics FROM sessions"
            params = []
            
            if filters:
                conditions = []
                for field, value in filters.items():
                    if field == 'start_time_min':
                        conditions.append("start_time >= ?")
                        params.append(value)
                    elif field == 'start_time_max':
                        conditions.append("start_time <= ?")
                        params.append(value)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY start_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [
                {
                    'id': row['id'],
                    'start_time': row['start_time'],
                    'spectral_metrics': json.loads(row['spectral_metrics']),
                    'catastrophe_metrics': json.loads(row['catastrophe_metrics']) if row['catastrophe_metrics'] else {}
                }
                for row in cursor.fetchall()
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving spectral metrics: {str(e)}")
            raise
        finally:
            conn.close()