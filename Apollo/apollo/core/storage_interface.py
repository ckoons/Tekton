"""
Apollo Storage Interface - Wrapper for ESR system integration.

Provides a unified interface for Apollo components to interact with either
the ESR memory system or legacy JSON storage, enabling gradual migration.
"""

import json
import logging
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class StorageMode:
    """Storage backend modes."""
    ESR = "esr"
    LEGACY = "legacy"
    HYBRID = "hybrid"  # Write to both, read from ESR with fallback


class ApolloStorageInterface:
    """
    Unified storage interface for Apollo components.
    
    Provides abstraction over ESR and legacy storage, allowing
    components to work with either backend transparently.
    """
    
    def __init__(self,
                 esr_system=None,
                 cognitive_workflows=None,
                 legacy_dir: Optional[str] = None,
                 mode: str = StorageMode.HYBRID):
        """
        Initialize storage interface.
        
        Args:
            esr_system: ESR memory system instance
            cognitive_workflows: Cognitive workflows instance
            legacy_dir: Directory for legacy JSON storage
            mode: Storage mode (esr, legacy, or hybrid)
        """
        self.esr_system = esr_system
        self.cognitive_workflows = cognitive_workflows
        self.legacy_dir = Path(legacy_dir) if legacy_dir else Path("/tmp/apollo_storage")
        self.mode = mode
        
        # Create legacy directory if needed
        if self.mode in [StorageMode.LEGACY, StorageMode.HYBRID]:
            self.legacy_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine available backends
        self.has_esr = esr_system is not None
        self.has_cognitive = cognitive_workflows is not None
        
        # Adjust mode based on availability
        if not self.has_esr and self.mode == StorageMode.ESR:
            logger.warning("ESR mode requested but ESR not available, falling back to legacy")
            self.mode = StorageMode.LEGACY
        
        logger.info(f"Storage interface initialized in {self.mode} mode")
    
    async def store_memory(self,
                          content: Any,
                          memory_type: str = "general",
                          metadata: Optional[Dict[str, Any]] = None,
                          ci_id: str = "apollo") -> str:
        """
        Store a memory item.
        
        Args:
            content: Memory content to store
            memory_type: Type of memory (insight, decision, error, etc.)
            metadata: Additional metadata
            ci_id: CI identifier
            
        Returns:
            Key/ID of stored memory
        """
        key = None
        metadata = metadata or {}
        metadata['memory_type'] = memory_type
        metadata['timestamp'] = datetime.now().isoformat()
        metadata['ci_id'] = ci_id
        
        # Store in ESR if available
        if self.has_cognitive and self.mode in [StorageMode.ESR, StorageMode.HYBRID]:
            try:
                # Use cognitive workflows for natural storage
                from engram.core.storage.cognitive_workflows import ThoughtType
                
                # Map memory types to thought types
                thought_type_map = {
                    'insight': ThoughtType.IDEA,
                    'decision': ThoughtType.PLAN,
                    'error': ThoughtType.OBSERVATION,
                    'fact': ThoughtType.FACT,
                    'opinion': ThoughtType.OPINION,
                    'question': ThoughtType.QUESTION
                }
                
                thought_type = thought_type_map.get(memory_type, ThoughtType.MEMORY)
                
                key = await self.cognitive_workflows.store_thought(
                    content=content,
                    thought_type=thought_type,
                    context=metadata,
                    ci_id=ci_id
                )
                
                logger.debug(f"Stored memory in ESR: {key[:8]}...")
                
            except Exception as e:
                logger.error(f"Failed to store in ESR: {e}")
                if self.mode == StorageMode.ESR:
                    raise
        
        # Store in legacy if needed
        if self.mode in [StorageMode.LEGACY, StorageMode.HYBRID]:
            try:
                # Generate key if not from ESR
                if not key:
                    import hashlib
                    content_str = json.dumps(content) if isinstance(content, dict) else str(content)
                    key = hashlib.sha256(content_str.encode()).hexdigest()[:16]
                
                # Prepare storage object
                storage_obj = {
                    'key': key,
                    'content': content,
                    'metadata': metadata
                }
                
                # Save to JSON file
                filename = self.legacy_dir / f"memory_{memory_type}_{key}.json"
                with open(filename, 'w') as f:
                    json.dump(storage_obj, f, indent=2, default=str)
                
                logger.debug(f"Stored memory in legacy: {filename.name}")
                
            except Exception as e:
                logger.error(f"Failed to store in legacy: {e}")
                if self.mode == StorageMode.LEGACY:
                    raise
        
        return key
    
    async def retrieve_memory(self,
                            key: str,
                            ci_id: str = "apollo") -> Optional[Any]:
        """
        Retrieve a specific memory by key.
        
        Args:
            key: Memory key/ID
            ci_id: CI identifier
            
        Returns:
            Memory content if found
        """
        result = None
        
        # Try ESR first if available
        if self.has_cognitive and self.mode in [StorageMode.ESR, StorageMode.HYBRID]:
            try:
                thought = await self.cognitive_workflows.recall_thought(
                    key=key,
                    ci_id=ci_id
                )
                
                if thought:
                    result = thought.content
                    logger.debug(f"Retrieved memory from ESR: {key[:8]}...")
                    
            except Exception as e:
                logger.error(f"Failed to retrieve from ESR: {e}")
        
        # Fall back to legacy if needed and no result yet
        if not result and self.mode in [StorageMode.LEGACY, StorageMode.HYBRID]:
            try:
                # Search for file with key
                pattern = f"memory_*_{key}.json"
                files = list(self.legacy_dir.glob(pattern))
                
                if files:
                    with open(files[0], 'r') as f:
                        data = json.load(f)
                        result = data.get('content')
                        logger.debug(f"Retrieved memory from legacy: {files[0].name}")
                        
            except Exception as e:
                logger.error(f"Failed to retrieve from legacy: {e}")
        
        return result
    
    async def search_memories(self,
                            query: str,
                            memory_type: Optional[str] = None,
                            limit: int = 10,
                            ci_id: str = "apollo") -> List[Dict[str, Any]]:
        """
        Search for memories matching a query.
        
        Args:
            query: Search query
            memory_type: Filter by memory type
            limit: Maximum results
            ci_id: CI identifier
            
        Returns:
            List of matching memories
        """
        results = []
        
        # Search ESR if available
        if self.has_esr and self.mode in [StorageMode.ESR, StorageMode.HYBRID]:
            try:
                # Use ESR search
                search_results = await self.esr_system.search(
                    query=query,
                    limit=limit,
                    filters={'memory_type': memory_type} if memory_type else None
                )
                
                for item in search_results:
                    results.append({
                        'content': item.get('content'),
                        'metadata': item.get('metadata', {}),
                        'score': item.get('score', 0.0)
                    })
                
                logger.debug(f"Found {len(results)} memories in ESR")
                
            except Exception as e:
                logger.error(f"Failed to search ESR: {e}")
        
        # Search legacy if needed and not enough results
        if len(results) < limit and self.mode in [StorageMode.LEGACY, StorageMode.HYBRID]:
            try:
                # Simple file-based search
                pattern = f"memory_{memory_type}_*.json" if memory_type else "memory_*.json"
                files = list(self.legacy_dir.glob(pattern))
                
                for file in files[:limit - len(results)]:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        content = data.get('content', {})
                        
                        # Simple text matching
                        content_str = json.dumps(content) if isinstance(content, dict) else str(content)
                        if query.lower() in content_str.lower():
                            results.append({
                                'content': content,
                                'metadata': data.get('metadata', {}),
                                'score': 0.5  # Fixed score for legacy
                            })
                
                logger.debug(f"Found {len(results)} total memories including legacy")
                
            except Exception as e:
                logger.error(f"Failed to search legacy: {e}")
        
        # Sort by score
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return results[:limit]
    
    async def build_context(self,
                          topic: str,
                          depth: int = 2,
                          ci_id: str = "apollo") -> Dict[str, Any]:
        """
        Build rich context around a topic.
        
        Args:
            topic: Topic to build context for
            depth: Depth of associations to follow
            ci_id: CI identifier
            
        Returns:
            Context dictionary
        """
        # Use cognitive workflows if available
        if self.has_cognitive and self.mode in [StorageMode.ESR, StorageMode.HYBRID]:
            try:
                context = await self.cognitive_workflows.build_context(
                    topic=topic,
                    depth=depth,
                    ci_id=ci_id
                )
                
                logger.info(f"Built context for '{topic}' using ESR")
                return context
                
            except Exception as e:
                logger.error(f"Failed to build context with ESR: {e}")
        
        # Fallback to simple search-based context
        logger.info(f"Building simple context for '{topic}'")
        
        memories = await self.search_memories(topic, limit=20, ci_id=ci_id)
        
        context = {
            'topic': topic,
            'memories': memories,
            'timestamp': datetime.now().isoformat(),
            'source': 'legacy' if self.mode == StorageMode.LEGACY else 'hybrid'
        }
        
        return context
    
    async def store_context_state(self,
                                 context_id: str,
                                 state: Dict[str, Any]) -> bool:
        """
        Store context state data.
        
        Args:
            context_id: Context identifier
            state: State data to store
            
        Returns:
            Success status
        """
        try:
            key = await self.store_memory(
                content=state,
                memory_type='context_state',
                metadata={'context_id': context_id}
            )
            return key is not None
            
        except Exception as e:
            logger.error(f"Failed to store context state: {e}")
            return False
    
    async def retrieve_context_state(self,
                                    context_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve context state data.
        
        Args:
            context_id: Context identifier
            
        Returns:
            State data if found
        """
        # Search for context state
        results = await self.search_memories(
            query=context_id,
            memory_type='context_state',
            limit=1
        )
        
        if results:
            return results[0].get('content')
        
        return None
    
    async def migrate_legacy_data(self) -> int:
        """
        Migrate legacy JSON data to ESR.
        
        Returns:
            Number of items migrated
        """
        if not self.has_esr:
            logger.error("Cannot migrate: ESR not available")
            return 0
        
        migrated = 0
        
        try:
            # Find all legacy JSON files
            files = list(self.legacy_dir.glob("memory_*.json"))
            
            for file in files:
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    # Store in ESR
                    await self.store_memory(
                        content=data.get('content'),
                        memory_type=data.get('metadata', {}).get('memory_type', 'general'),
                        metadata={**data.get('metadata', {}), 'migrated': True},
                        ci_id=data.get('metadata', {}).get('ci_id', 'apollo')
                    )
                    
                    migrated += 1
                    logger.debug(f"Migrated {file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to migrate {file.name}: {e}")
            
            logger.info(f"Migrated {migrated} items from legacy to ESR")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
        
        return migrated
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            'mode': self.mode,
            'has_esr': self.has_esr,
            'has_cognitive': self.has_cognitive
        }
        
        # Get ESR stats if available
        if self.has_cognitive:
            stats['esr_stats'] = self.cognitive_workflows.get_memory_stats()
        
        # Count legacy files
        if self.mode in [StorageMode.LEGACY, StorageMode.HYBRID]:
            try:
                files = list(self.legacy_dir.glob("memory_*.json"))
                stats['legacy_count'] = len(files)
            except:
                stats['legacy_count'] = 0
        
        return stats