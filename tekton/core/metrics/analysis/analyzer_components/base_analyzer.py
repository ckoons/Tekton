#!/usr/bin/env python3
"""
Base spectral analyzer classes and interfaces.

This module defines the base classes for spectral analysis functionality.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union

from ...utils import session_to_dict

logger = logging.getLogger(__name__)


class BaseAnalyzer:
    """Base class for all spectral analyzers."""
    
    def __init__(self, storage=None):
        """Initialize spectral analyzer.
        
        Args:
            storage: Optional metrics storage engine
        """
        self.storage = storage
    
    def analyze_session(self, session_data):
        """Analyze a single session.
        
        Args:
            session_data: SessionData object or dict
            
        Returns:
            Dict of analysis results
        """
        raise NotImplementedError("Subclasses must implement analyze_session")
    
    def analyze_sessions(self, sessions, group_by=None):
        """Analyze multiple sessions with optional grouping.
        
        Args:
            sessions: List of SessionData objects or dicts
            group_by: Optional field to group sessions by
            
        Returns:
            Dict of analysis results
        """
        raise NotImplementedError("Subclasses must implement analyze_sessions")
