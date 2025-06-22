"""
Landmark Registry - Central management of all landmarks
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
import threading
from collections import defaultdict

from .landmark import Landmark


class LandmarkRegistry:
    """
    Central registry for all landmarks in the Tekton system.
    Provides storage, retrieval, and search capabilities.
    """
    
    # Class-level storage
    _instance = None
    _lock = threading.Lock()
    _landmarks: Dict[str, Landmark] = {}
    _index: Dict[str, Dict[str, Set[str]]] = {
        'type': defaultdict(set),
        'component': defaultdict(set),
        'file': defaultdict(set),
        'tag': defaultdict(set)
    }
    _storage_path = Path("/Users/cskoons/projects/github/Tekton/landmarks/data")
    _registry_file = _storage_path / "registry.json"
    
    def __new__(cls):
        """Singleton pattern for registry"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the registry"""
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._load_registry()
    
    @classmethod
    def register(cls, landmark: Landmark) -> None:
        """Register a new landmark"""
        instance = cls()
        
        # Store landmark
        cls._landmarks[landmark.id] = landmark
        
        # Update indexes
        cls._index['type'][landmark.type].add(landmark.id)
        cls._index['component'][landmark.component].add(landmark.id)
        cls._index['file'][landmark.file_path].add(landmark.id)
        
        # Update tags index
        for tag in landmark.tags:
            cls._index['tag'][tag].add(landmark.id)
        
        # Save to disk
        instance._save_landmark(landmark)
        instance._save_registry()
    
    @classmethod
    def get(cls, landmark_id: str) -> Optional[Landmark]:
        """Get a landmark by ID"""
        return cls._landmarks.get(landmark_id)
    
    @classmethod
    def list(cls, type: Optional[str] = None, 
             component: Optional[str] = None,
             file_path: Optional[str] = None,
             tags: Optional[List[str]] = None) -> List[Landmark]:
        """List landmarks with optional filters"""
        result_ids = set(cls._landmarks.keys())
        
        # Apply filters
        if type:
            result_ids &= cls._index['type'].get(type, set())
        
        if component:
            result_ids &= cls._index['component'].get(component, set())
            
        if file_path:
            result_ids &= cls._index['file'].get(file_path, set())
            
        if tags:
            for tag in tags:
                result_ids &= cls._index['tag'].get(tag, set())
        
        # Return landmarks sorted by timestamp
        landmarks = [cls._landmarks[lid] for lid in result_ids]
        return sorted(landmarks, key=lambda l: l.timestamp, reverse=True)
    
    @classmethod
    def search(cls, query: str) -> List[Landmark]:
        """
        Search landmarks by text in title, description, or metadata.
        Simple text search for now, can be enhanced with semantic search later.
        """
        query_lower = query.lower()
        results = []
        
        for landmark in cls._landmarks.values():
            # Search in various fields
            if any([
                query_lower in landmark.title.lower(),
                query_lower in landmark.description.lower(),
                query_lower in str(landmark.metadata).lower(),
                query_lower in landmark.type.lower(),
                any(query_lower in tag.lower() for tag in landmark.tags)
            ]):
                results.append(landmark)
        
        return sorted(results, key=lambda l: l.timestamp, reverse=True)
    
    @classmethod
    def get_by_location(cls, file_path: str, line_number: int, 
                       tolerance: int = 10) -> List[Landmark]:
        """Get landmarks near a specific location in code"""
        results = []
        
        file_landmarks = cls._index['file'].get(file_path, set())
        for lid in file_landmarks:
            landmark = cls._landmarks[lid]
            if abs(landmark.line_number - line_number) <= tolerance:
                results.append(landmark)
        
        return sorted(results, key=lambda l: abs(l.line_number - line_number))
    
    @classmethod
    def get_related(cls, landmark_id: str) -> List[Landmark]:
        """Get landmarks related to a given landmark"""
        landmark = cls.get(landmark_id)
        if not landmark:
            return []
        
        related = []
        for related_id in landmark.related_landmarks:
            related_landmark = cls.get(related_id)
            if related_landmark:
                related.append(related_landmark)
        
        return related
    
    def _save_landmark(self, landmark: Landmark) -> None:
        """Save individual landmark to disk"""
        landmark_file = self._storage_path / f"{landmark.id}.json"
        with open(landmark_file, 'w') as f:
            json.dump(landmark.to_dict(), f, indent=2)
    
    def _save_registry(self) -> None:
        """Save registry index to disk"""
        registry_data = {
            'version': '1.0',
            'updated': datetime.now().isoformat(),
            'landmark_count': len(self._landmarks),
            'landmark_ids': list(self._landmarks.keys()),
            'indexes': {
                'by_type': {k: list(v) for k, v in self._index['type'].items()},
                'by_component': {k: list(v) for k, v in self._index['component'].items()},
                'by_tag': {k: list(v) for k, v in self._index['tag'].items()}
            }
        }
        
        with open(self._registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
    
    def _load_registry(self) -> None:
        """Load registry from disk"""
        if not self._registry_file.exists():
            return
        
        try:
            with open(self._registry_file, 'r') as f:
                registry_data = json.load(f)
            
            # Load each landmark
            for landmark_id in registry_data.get('landmark_ids', []):
                landmark_file = self._storage_path / f"{landmark_id}.json"
                if landmark_file.exists():
                    with open(landmark_file, 'r') as f:
                        landmark_data = json.load(f)
                        landmark = Landmark.from_dict(landmark_data)
                        
                        # Store in memory
                        self._landmarks[landmark.id] = landmark
                        
                        # Rebuild indexes
                        self._index['type'][landmark.type].add(landmark.id)
                        self._index['component'][landmark.component].add(landmark.id)
                        self._index['file'][landmark.file_path].add(landmark.id)
                        for tag in landmark.tags:
                            self._index['tag'][tag].add(landmark.id)
                            
        except Exception as e:
            print(f"Error loading registry: {e}")
    
    @classmethod
    def stats(cls) -> Dict[str, Any]:
        """Get registry statistics"""
        type_counts = {t: len(ids) for t, ids in cls._index['type'].items()}
        component_counts = {c: len(ids) for c, ids in cls._index['component'].items()}
        
        return {
            'total_landmarks': len(cls._landmarks),
            'by_type': type_counts,
            'by_component': component_counts,
            'total_files': len(cls._index['file']),
            'total_tags': len(cls._index['tag'])
        }
    
    @classmethod
    def clear(cls) -> None:
        """Clear all landmarks (use with caution!)"""
        cls._landmarks.clear()
        cls._index.clear()
        
        # Clear storage
        if cls._storage_path.exists():
            for file in cls._storage_path.glob('*.json'):
                file.unlink()


# Convenience functions for module-level access
def register_landmark(landmark: Landmark) -> None:
    """Register a landmark"""
    LandmarkRegistry.register(landmark)


def get_landmark(landmark_id: str) -> Optional[Landmark]:
    """Get a landmark by ID"""
    return LandmarkRegistry.get(landmark_id)


def search_landmarks(query: str) -> List[Landmark]:
    """Search landmarks"""
    return LandmarkRegistry.search(query)


def list_landmarks(**filters) -> List[Landmark]:
    """List landmarks with filters"""
    return LandmarkRegistry.list(**filters)