"""
Base class for metrics storage.
"""

from typing import Dict, List, Any, Optional

class MetricsStorage:
    """Base class for metrics storage."""
    
    def store_session(self, session_data):
        """Store a session's metrics data.
        
        Args:
            session_data: The session data to store
        """
        raise NotImplementedError("Subclasses must implement store_session")
    
    def get_session(self, session_id):
        """Retrieve a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session data dict or None if not found
        """
        raise NotImplementedError("Subclasses must implement get_session")
    
    def get_sessions(self, filters=None, limit=100, offset=0):
        """Retrieve multiple sessions with optional filtering.
        
        Args:
            filters: Optional dict of filters to apply
            limit: Maximum number of sessions to retrieve
            offset: Offset for pagination
            
        Returns:
            List of session data dicts
        """
        raise NotImplementedError("Subclasses must implement get_sessions")
    
    def get_spectral_metrics(self, filters=None, limit=100):
        """Get spectral metrics for multiple sessions.
        
        Args:
            filters: Optional dict of filters to apply
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of spectral metrics data
        """
        raise NotImplementedError("Subclasses must implement get_spectral_metrics")