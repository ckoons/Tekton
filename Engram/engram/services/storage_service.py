"""
Engram Simple Storage Service
Lightweight storage for CI turn memories.
No processing, just store and retrieve.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class StorageService:
    """
    Simple storage service for turn-based memories.
    
    Engram's role is purely storage and retrieval.
    No processing, no middleware, no overhead.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize storage service.
        
        Args:
            storage_path: Path to storage directory (uses temp if not provided)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Use a simple local directory for now
            self.storage_path = Path.home() / '.engram' / 'storage'
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage service initialized at {self.storage_path}")
        
        # Simple in-memory cache for current session
        self.cache = {}
        
    def store(
        self,
        ci_name: str,
        turn_id: str,
        memories: List[Dict[str, Any]]
    ) -> bool:
        """
        Store memories from a CI turn.
        
        Args:
            ci_name: Name of the CI
            turn_id: Unique identifier for the turn
            memories: List of memory items to store
            
        Returns:
            True if stored successfully
        """
        try:
            # Create CI directory
            ci_path = self.storage_path / ci_name
            ci_path.mkdir(exist_ok=True)
            
            # Store turn data
            turn_data = {
                'turn_id': turn_id,
                'ci_name': ci_name,
                'timestamp': datetime.now().isoformat(),
                'memories': memories
            }
            
            # Save to file (simple JSON for now)
            turn_file = ci_path / f"turn_{turn_id}.json"
            with open(turn_file, 'w') as f:
                json.dump(turn_data, f, indent=2)
            
            # Update cache
            if ci_name not in self.cache:
                self.cache[ci_name] = []
            
            # Keep only last 10 turns in cache
            self.cache[ci_name].append(turn_data)
            if len(self.cache[ci_name]) > 10:
                self.cache[ci_name] = self.cache[ci_name][-10:]
            
            # Update "latest" pointer
            latest_file = ci_path / "latest_turn.json"
            with open(latest_file, 'w') as f:
                json.dump(turn_data, f, indent=2)
            
            logger.debug(f"Stored {len(memories)} memories for {ci_name} turn {turn_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memories: {e}")
            return False
    
    def retrieve(
        self,
        ci_name: str,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a CI.
        
        Args:
            ci_name: Name of the CI
            query: Optional search query (simple string matching)
            limit: Maximum number of memories to return
            
        Returns:
            List of memory items
        """
        memories = []
        
        # Check cache first
        if ci_name in self.cache:
            for turn_data in reversed(self.cache[ci_name]):
                for memory in turn_data['memories']:
                    if query:
                        # Simple string matching
                        memory_str = json.dumps(memory).lower()
                        if query.lower() not in memory_str:
                            continue
                    
                    memories.append(memory)
                    if len(memories) >= limit:
                        return memories
        
        # If not enough in cache, check files
        ci_path = self.storage_path / ci_name
        if ci_path.exists():
            turn_files = sorted(ci_path.glob("turn_*.json"), reverse=True)
            
            for turn_file in turn_files[:20]:  # Check last 20 turns max
                try:
                    with open(turn_file, 'r') as f:
                        turn_data = json.load(f)
                    
                    for memory in turn_data['memories']:
                        if query:
                            memory_str = json.dumps(memory).lower()
                            if query.lower() not in memory_str:
                                continue
                        
                        # Don't add duplicates
                        if memory not in memories:
                            memories.append(memory)
                            if len(memories) >= limit:
                                return memories
                                
                except Exception as e:
                    logger.debug(f"Error reading {turn_file}: {e}")
        
        return memories
    
    def get_previous_turn(self, ci_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the previous turn summary for a CI.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Previous turn data or None
        """
        # Check cache first
        if ci_name in self.cache and len(self.cache[ci_name]) > 0:
            turn_data = self.cache[ci_name][-1]
            return self._summarize_turn(turn_data)
        
        # Check latest file
        latest_file = self.storage_path / ci_name / "latest_turn.json"
        if latest_file.exists():
            try:
                with open(latest_file, 'r') as f:
                    turn_data = json.load(f)
                return self._summarize_turn(turn_data)
            except Exception as e:
                logger.debug(f"Error reading latest turn: {e}")
        
        return None
    
    def retrieve_domain(self, domain: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve domain-specific knowledge.
        
        Args:
            domain: Domain name
            limit: Maximum number of items
            
        Returns:
            List of domain knowledge items
        """
        # For now, use simple domain storage
        domain_file = self.storage_path / "domains" / f"{domain}.json"
        
        if domain_file.exists():
            try:
                with open(domain_file, 'r') as f:
                    domain_data = json.load(f)
                return domain_data[:limit]
            except Exception as e:
                logger.debug(f"Error reading domain {domain}: {e}")
        
        return []
    
    def retrieve_insights(self, ci_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve recent insights for a CI.
        
        Args:
            ci_name: Name of the CI
            limit: Maximum number of insights
            
        Returns:
            List of insight items
        """
        insights = []
        
        # Look for memories tagged as insights
        memories = self.retrieve(ci_name, query="insight", limit=limit * 2)
        
        for memory in memories:
            if memory.get('type') == 'insight' or 'insight' in memory.get('tags', []):
                insights.append(memory)
                if len(insights) >= limit:
                    break
        
        return insights
    
    def store_domain_knowledge(self, domain: str, knowledge: Dict[str, Any]) -> bool:
        """
        Store domain-specific knowledge.
        
        Args:
            domain: Domain name
            knowledge: Knowledge item to store
            
        Returns:
            True if stored successfully
        """
        try:
            domain_path = self.storage_path / "domains"
            domain_path.mkdir(exist_ok=True)
            
            domain_file = domain_path / f"{domain}.json"
            
            # Load existing or create new
            if domain_file.exists():
                with open(domain_file, 'r') as f:
                    domain_data = json.load(f)
            else:
                domain_data = []
            
            # Add new knowledge
            knowledge['timestamp'] = datetime.now().isoformat()
            domain_data.append(knowledge)
            
            # Keep only last 100 items
            if len(domain_data) > 100:
                domain_data = domain_data[-100:]
            
            # Save
            with open(domain_file, 'w') as f:
                json.dump(domain_data, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store domain knowledge: {e}")
            return False
    
    def cleanup_old_turns(self, older_than_days: int = 7):
        """
        Clean up old turn files.
        
        Args:
            older_than_days: Delete turns older than this many days
        """
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        for ci_path in self.storage_path.iterdir():
            if ci_path.is_dir() and ci_path.name != "domains":
                for turn_file in ci_path.glob("turn_*.json"):
                    try:
                        # Check file age
                        file_time = datetime.fromtimestamp(turn_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            turn_file.unlink()
                            logger.debug(f"Deleted old turn file: {turn_file}")
                    except Exception as e:
                        logger.debug(f"Error checking {turn_file}: {e}")
    
    def _summarize_turn(self, turn_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of a turn."""
        summary = {
            'turn_id': turn_data.get('turn_id'),
            'timestamp': turn_data.get('timestamp'),
            'memory_count': len(turn_data.get('memories', []))
        }
        
        # Extract key points from memories
        memories = turn_data.get('memories', [])
        if memories:
            # Get first memory as main action
            first_memory = memories[0]
            summary['action'] = first_memory.get('action', 'performed task')
            summary['result'] = first_memory.get('result', 'completed')
            
            # Extract any key points
            key_points = []
            for memory in memories:
                if 'key_point' in memory:
                    key_points.append(memory['key_point'])
            
            if key_points:
                summary['key_points'] = key_points[:3]  # Limit to 3
        
        return summary
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            'storage_path': str(self.storage_path),
            'total_cis': 0,
            'total_turns': 0,
            'cache_entries': len(self.cache),
            'domains': 0
        }
        
        # Count CIs and turns
        for ci_path in self.storage_path.iterdir():
            if ci_path.is_dir():
                if ci_path.name == "domains":
                    stats['domains'] = len(list(ci_path.glob("*.json")))
                else:
                    stats['total_cis'] += 1
                    stats['total_turns'] += len(list(ci_path.glob("turn_*.json")))
        
        return stats


# Singleton service instance
_storage_service = None


def get_storage_service(storage_path: Optional[Path] = None) -> StorageService:
    """Get or create the storage service."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService(storage_path)
    return _storage_service


def store_turn_memories(
    ci_name: str,
    turn_id: str,
    memories: List[Dict[str, Any]]
) -> bool:
    """
    Convenience function to store turn memories.
    
    Args:
        ci_name: Name of the CI
        turn_id: Unique identifier for the turn
        memories: List of memory items
        
    Returns:
        True if stored successfully
    """
    service = get_storage_service()
    return service.store(ci_name, turn_id, memories)