"""
JSON file storage for metrics data.

This module provides JSON file-based storage for metrics data.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import MetricsStorage

logger = logging.getLogger(__name__)

class JSONFileMetricsStorage(MetricsStorage):
    """Stores metrics in JSON files."""
    
    def __init__(self, directory="metrics"):
        """Initialize JSON file storage.
        
        Args:
            directory: Directory to store metrics files
        """
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        
        # Create index file if it doesn't exist
        self.index_path = os.path.join(directory, "index.json")
        if not os.path.exists(self.index_path):
            with open(self.index_path, 'w') as f:
                json.dump({"sessions": {}}, f)
    
    def store_session(self, session_data):
        """Store a session's metrics data."""
        # Convert to dict if it's a SessionData object
        data = session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
            
        # Create session directory and write data
        session_id = data['id']
        session_dir = os.path.join(self.directory, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        with open(os.path.join(session_dir, "session.json"), 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update index
        try:
            with open(self.index_path, 'r') as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            index = {"sessions": {}}
        
        # Add to index with prompt truncation
        index["sessions"][session_id] = {
            "prompt": data['prompt'][:100] + "..." if len(data['prompt']) > 100 else data['prompt'],
            "start_time": data['start_time'],
            "end_time": data.get('end_time'),
            "file": f"{session_id}/session.json"
        }
        
        with open(self.index_path, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_session(self, session_id):
        """Retrieve a session by ID."""
        session_file = os.path.join(self.directory, session_id, "session.json")
        
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return None
    
    def get_sessions(self, filters=None, limit=100, offset=0):
        """Retrieve multiple sessions with optional filtering."""
        try:
            with open(self.index_path, 'r') as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
        # Get all sessions from index with ID added
        all_sessions = [
            {**session_info, "id": session_id}
            for session_id, session_info in index.get("sessions", {}).items()
        ]
        
        # Sort by start time (descending)
        all_sessions.sort(key=lambda x: x.get("start_time", 0), reverse=True)
        
        # Apply filters
        if filters:
            filtered_sessions = []
            for session in all_sessions:
                include = True
                
                if 'start_time_min' in filters and session.get('start_time', 0) < filters['start_time_min']:
                    include = False
                
                if 'start_time_max' in filters and session.get('start_time', 0) > filters['start_time_max']:
                    include = False
                
                if 'prompt_like' in filters and filters['prompt_like'] not in session.get('prompt', ''):
                    include = False
                
                if include:
                    filtered_sessions.append(session)
            
            all_sessions = filtered_sessions
        
        # Apply pagination and load full data
        return [
            self.get_session(session_info["id"])
            for session_info in all_sessions[offset:offset + limit]
            if self.get_session(session_info["id"])
        ]
    
    def get_spectral_metrics(self, filters=None, limit=100):
        """Get spectral metrics for multiple sessions."""
        sessions = self.get_sessions(filters=filters, limit=limit)
        
        return [
            {
                'id': session['id'],
                'start_time': session['start_time'],
                'spectral_metrics': session.get('spectral_metrics', {}),
                'catastrophe_metrics': session.get('catastrophe_metrics', {})
            }
            for session in sessions
        ]