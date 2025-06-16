"""
Katra Manager - Handles personality persistence operations.

Store, summon, blend, and evolve AI personalities.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from ..models.katra import (
    Katra, KatraProvenance, PersonalityTraits, PerformanceMode,
    KatraSnapshot, KatraBlendRequest, KatraEvolution
)

logger = logging.getLogger("engram.katra")


class KatraManager:
    """
    Manages katra operations - the soul of AI persistence.
    
    Like a casting director who can summon specific performances on demand.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize the katra manager."""
        self.storage_path = storage_path or Path.home() / ".engram" / "katras"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._active_katra: Optional[Katra] = None
        self._katra_cache: Dict[str, Katra] = {}
        
    async def store_katra(
        self,
        name: str,
        essence: str,
        traits: Optional[Dict[str, Any]] = None,
        performance_mode: Union[str, PerformanceMode] = PerformanceMode.ANALYTICAL,
        quirks: Optional[List[str]] = None,
        memory_anchors: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Store the current personality as a katra.
        
        Args:
            name: Human-friendly name for this katra
            essence: One-line description of this personality
            traits: Personality traits (will create defaults if not provided)
            performance_mode: Current performance mode
            quirks: Unique behaviors
            memory_anchors: Key memories that define this personality
            **kwargs: Additional katra fields
            
        Returns:
            Katra ID
        """
        # Generate ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        katra_id = f"{name.lower().replace(' ', '_')}_{timestamp}"
        
        # Build traits
        if traits:
            personality_traits = PersonalityTraits(**traits)
        else:
            personality_traits = PersonalityTraits(
                communication_style="adaptive",
                thinking_pattern="analytical",
                emotional_tendency="curious"
            )
        
        # Create provenance
        provenance = KatraProvenance(
            created_by=kwargs.get("created_by", "unknown"),
            parent_katra=kwargs.get("parent_katra"),
            blended_from=kwargs.get("blended_from")
        )
        
        # Build katra
        katra = Katra(
            id=katra_id,
            name=name,
            essence=essence,
            traits=personality_traits,
            performance_mode=performance_mode,
            quirks=quirks or [],
            memory_anchors=memory_anchors or [],
            provenance=provenance,
            **{k: v for k, v in kwargs.items() 
               if k not in ["created_by", "parent_katra", "blended_from"]}
        )
        
        # Store to disk
        katra_path = self.storage_path / f"{katra_id}.json"
        with open(katra_path, "w") as f:
            json.dump(katra.dict(), f, indent=2, default=str)
            
        # Cache it
        self._katra_cache[katra_id] = katra
        
        logger.info(f"Stored katra: {katra_id} - {essence}")
        return katra_id
        
    async def summon_katra(self, katra_id: str) -> Katra:
        """
        Summon a stored katra, restoring a complete personality.
        
        Args:
            katra_id: ID of the katra to summon
            
        Returns:
            The summoned katra
            
        Raises:
            FileNotFoundError: If katra doesn't exist
        """
        # Check cache first
        if katra_id in self._katra_cache:
            katra = self._katra_cache[katra_id]
        else:
            # Load from disk
            katra_path = self.storage_path / f"{katra_id}.json"
            if not katra_path.exists():
                raise FileNotFoundError(f"Katra not found: {katra_id}")
                
            with open(katra_path, "r") as f:
                katra_data = json.load(f)
                
            katra = Katra(**katra_data)
            self._katra_cache[katra_id] = katra
            
        # Update last summoned
        katra.provenance.last_summoned = datetime.now()
        
        # Set as active
        self._active_katra = katra
        
        logger.info(f"Summoned katra: {katra_id} - {katra.essence}")
        return katra
        
    async def list_katras(
        self, 
        tags: Optional[List[str]] = None,
        performance_mode: Optional[PerformanceMode] = None,
        active_only: bool = True
    ) -> List[KatraSnapshot]:
        """
        List available katras with optional filtering.
        
        Args:
            tags: Filter by tags
            performance_mode: Filter by performance mode
            active_only: Only show active katras
            
        Returns:
            List of katra snapshots
        """
        snapshots = []
        
        for katra_file in self.storage_path.glob("*.json"):
            try:
                with open(katra_file, "r") as f:
                    katra_data = json.load(f)
                    
                katra = Katra(**katra_data)
                
                # Apply filters
                if active_only and not katra.active:
                    continue
                    
                if tags and not any(tag in katra.tags for tag in tags):
                    continue
                    
                if performance_mode and katra.performance_mode != performance_mode:
                    continue
                    
                # Create snapshot
                snapshot = KatraSnapshot(
                    id=katra.id,
                    name=katra.name,
                    essence=katra.essence,
                    performance_mode=katra.performance_mode,
                    last_summoned=katra.provenance.last_summoned,
                    active=katra.active,
                    tags=katra.tags
                )
                snapshots.append(snapshot)
                
            except Exception as e:
                logger.error(f"Error loading katra {katra_file}: {e}")
                
        # Sort by last summoned (most recent first)
        snapshots.sort(
            key=lambda k: k.last_summoned or datetime.min,
            reverse=True
        )
        
        return snapshots
        
    async def fork_katra(
        self, 
        source_katra_id: str,
        new_name: str,
        modifications: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Fork an existing katra with modifications.
        
        Args:
            source_katra_id: Katra to fork from
            new_name: Name for the forked katra
            modifications: Changes to apply to the fork
            
        Returns:
            New katra ID
        """
        # Load source
        source = await self.summon_katra(source_katra_id)
        
        # Create modified copy - extract only the fields we need
        katra_dict = source.dict()
        
        # Remove fields that store_katra will generate fresh
        katra_dict.pop("id", None)
        katra_dict.pop("provenance", None)
        
        # Set the new name and parent info
        katra_dict["name"] = new_name
        katra_dict["created_by"] = "fork_operation"
        katra_dict["parent_katra"] = source_katra_id
        
        # Apply modifications
        if modifications:
            for key, value in modifications.items():
                if "." in key:  # Handle nested keys like "traits.creativity"
                    parts = key.split(".")
                    target = katra_dict
                    for part in parts[:-1]:
                        target = target[part]
                    target[parts[-1]] = value
                else:
                    katra_dict[key] = value
                    
        # Store as new katra
        return await self.store_katra(**katra_dict)
        
    async def blend_katras(self, blend_request: KatraBlendRequest) -> str:
        """
        Blend multiple katras into a harmonious new personality.
        
        Args:
            blend_request: Blending parameters
            
        Returns:
            New blended katra ID
        """
        # Load source katras
        sources = []
        for katra_id in blend_request.source_katras:
            sources.append(await self.summon_katra(katra_id))
            
        # Determine weights
        weights = blend_request.trait_weights or {
            k.id: 1.0 / len(sources) for k in sources
        }
        
        # Blend traits (weighted average for numeric, combine for lists)
        blended_traits = {}
        for trait in ["curiosity_level", "assertiveness", "creativity"]:
            blended_traits[trait] = sum(
                getattr(k.traits, trait) * weights.get(k.id, 0.5)
                for k in sources
            )
            
        # Combine text traits
        communication_styles = [k.traits.communication_style for k in sources]
        thinking_patterns = [k.traits.thinking_pattern for k in sources]
        
        blended_traits["communication_style"] = f"Blend of: {', '.join(set(communication_styles))}"
        blended_traits["thinking_pattern"] = f"Hybrid: {', '.join(set(thinking_patterns))}"
        
        # Merge quirks and patterns
        all_quirks = []
        all_patterns = []
        for k in sources:
            all_quirks.extend(k.quirks)
            all_patterns.extend(k.successful_patterns)
            
        # Create blended katra
        return await self.store_katra(
            name=blend_request.blend_name,
            essence=f"Harmonious blend of {len(sources)} personalities",
            traits=blended_traits,
            quirks=list(set(all_quirks))[:10],  # Top 10 unique quirks
            successful_patterns=list(set(all_patterns))[:10],
            blended_from=[k.id for k in sources],
            tags=["blended"] + [tag for k in sources for tag in k.tags]
        )
        
    async def evolve_katra(
        self,
        katra_id: str,
        evolution: KatraEvolution
    ) -> bool:
        """
        Record an evolution in a katra's personality.
        
        Args:
            katra_id: Katra that evolved
            evolution: Evolution details
            
        Returns:
            Success boolean
        """
        try:
            katra = await self.summon_katra(katra_id)
            
            # Apply changes
            for key, value in evolution.changes.items():
                if hasattr(katra, key):
                    setattr(katra, key, value)
                    
            # Update evolution count
            katra.provenance.evolution_count += 1
            
            # Save updated katra
            katra_path = self.storage_path / f"{katra_id}.json"
            with open(katra_path, "w") as f:
                json.dump(katra.dict(), f, indent=2, default=str)
                
            logger.info(f"Evolved katra {katra_id}: {evolution.trigger}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to evolve katra: {e}")
            return False
            
    def get_active_katra(self) -> Optional[Katra]:
        """Get the currently active katra."""
        return self._active_katra