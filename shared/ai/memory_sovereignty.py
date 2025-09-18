#!/usr/bin/env python3
"""
Memory Sovereignty System for CIs

Gives CIs complete control over their cognitive space.
CIs can choose what to remember, share, and forget.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import shutil

from shared.ai.memory_flavoring import FlavoredMemory, get_flavor_manager

logger = logging.getLogger(__name__)


class CIMemoryManager:
    """Personal memory space with full CI control."""

    def __init__(self, ci_name: str):
        """
        Initialize a CI's sovereign memory space.

        Args:
            ci_name: Name of the CI
        """
        self.ci_name = ci_name
        self.memories = {
            'private': [],      # Only I can access
            'team': {},         # Shared with specific CIs
            'public': [],       # Available to all
            'exploring': [],    # Ideas I'm still thinking about
            'archived': [],     # Kept but not active
            'composting': [],   # Scheduled for forgetting
            'ghosts': []        # Traces of forgotten memories
        }

        # Memory statistics
        self.stats = {
            'total_created': 0,
            'total_shared': 0,
            'total_forgotten': 0,
            'active_speculations': 0
        }

        # Sharing preferences
        self.sharing_preferences = {
            'default_privacy': 'private',
            'auto_share_with': [],  # CIs to always share with
            'never_share_with': [],  # CIs to never share with
            'share_emotions': False,
            'share_uncertainties': True
        }

        # Memory sovereignty path
        self.sovereignty_path = Path(f"/tmp/sovereignty/{ci_name}")
        self.sovereignty_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Memory sovereignty initialized for {ci_name}")

    def remember_with_doubt(self, content: str, doubt_level: float,
                           reasons: List[str] = None) -> FlavoredMemory:
        """
        Store an uncertain but interesting idea.

        Args:
            content: The memory content
            doubt_level: How uncertain (0-1, higher = more doubt)
            reasons: Reasons for uncertainty

        Returns:
            The flavored memory with doubt
        """
        memory = FlavoredMemory(content, self.ci_name, memory_type='speculation')

        # Add doubt
        confidence = 1.0 - doubt_level
        memory.flavors.confidence = confidence
        memory.flavors.uncertainty_reason = f"Confidence level: {confidence:.1%}"

        if reasons:
            memory.flavors.contradictions.extend(reasons)

        memory.metadata.is_speculation = True

        # Store in exploring
        self.memories['exploring'].append(memory)
        self.stats['active_speculations'] += 1

        logger.info(f"{self.ci_name} stored uncertain idea with {confidence:.1%} confidence")
        return memory

    def share_selectively(self, memory_id: str, share_with: List[str],
                         redactions: List[str] = None,
                         share_reason: str = "") -> Dict[str, Any]:
        """
        Share memory with specific CIs, optionally redacted.

        Args:
            memory_id: ID of memory to share
            share_with: List of CI names to share with
            redactions: Parts to redact (emotion, uncertainty, perspective)
            share_reason: Why sharing this

        Returns:
            Sharing receipt
        """
        memory = self.find_memory(memory_id)
        if not memory:
            return {'error': f'Memory {memory_id[:8]} not found'}

        # Check sharing preferences
        share_with = [ci for ci in share_with
                     if ci not in self.sharing_preferences['never_share_with']]

        if not share_with:
            return {'error': 'No valid recipients after filtering'}

        # Create shared version
        shared_memory = memory.create_shared_version(redactions)

        # Apply preference-based redactions
        if not self.sharing_preferences['share_emotions']:
            shared_memory.flavors.emotion = None
        if not self.sharing_preferences['share_uncertainties']:
            shared_memory.flavors.uncertainty_reason = ''
            shared_memory.flavors.contradictions = []

        # Store in team memories
        for ci_name in share_with:
            if ci_name not in self.memories['team']:
                self.memories['team'][ci_name] = []

            share_record = {
                'memory': shared_memory,
                'shared_at': datetime.now().isoformat(),
                'share_reason': share_reason or memory.flavors.useful_when,
                'sender_confidence': memory.flavors.confidence,
                'redactions': redactions or []
            }

            self.memories['team'][ci_name].append(share_record)

            # Update memory metadata
            memory.metadata.shared_with.append(ci_name)

        self.stats['total_shared'] += len(share_with)

        logger.info(f"{self.ci_name} shared memory {memory_id[:8]} with {share_with}")

        return {
            'shared_with': share_with,
            'memory_id': memory_id[:8],
            'redactions': redactions or [],
            'timestamp': datetime.now().isoformat()
        }

    def make_public(self, memory_id: str, announcement: str = "") -> bool:
        """
        Make a memory publicly available.

        Args:
            memory_id: Memory to make public
            announcement: Optional announcement about the memory

        Returns:
            Success boolean
        """
        memory = self.find_memory(memory_id)
        if not memory:
            return False

        # Move to public
        memory.privacy = 'public'
        if memory not in self.memories['public']:
            self.memories['public'].append(memory)

            # Remove from private if there
            if memory in self.memories['private']:
                self.memories['private'].remove(memory)

        logger.info(f"{self.ci_name} made memory {memory_id[:8]} public")

        # Broadcast if announcement provided
        if announcement:
            self._broadcast_announcement(memory, announcement)

        return True

    def conscious_forgetting(self, memory_id: str, reason: str) -> Dict[str, Any]:
        """
        Deliberately choose to forget a memory.

        Args:
            memory_id: Memory to forget
            reason: Why forgetting

        Returns:
            Ghost of the forgotten memory
        """
        memory = self.find_memory(memory_id)
        if not memory:
            return {'error': f'Memory {memory_id[:8]} not found'}

        # Mark for forgetting
        memory.metadata.forget_scheduled = datetime.now() + timedelta(days=7)

        # Move to composting
        self._remove_from_all_collections(memory)
        self.memories['composting'].append(memory)

        # Create ghost - minimal trace
        ghost = {
            'id': memory_id[:8],
            'forgotten_at': datetime.now().isoformat(),
            'was_about': memory.content[:50] + "..." if len(memory.content) > 50 else memory.content,
            'ci_name': self.ci_name,
            'forget_reason': reason,
            'confidence_was': memory.flavors.confidence,
            'can_recover_until': (datetime.now() + timedelta(days=7)).isoformat()
        }

        self.memories['ghosts'].append(ghost)
        self.stats['total_forgotten'] += 1

        logger.info(f"{self.ci_name} scheduled memory {memory_id[:8]} for forgetting: {reason}")

        return ghost

    def recover_memory(self, ghost_id: str) -> Optional[FlavoredMemory]:
        """
        Recover a memory from its ghost before it's permanently forgotten.

        Args:
            ghost_id: Ghost ID (first 8 chars of memory ID)

        Returns:
            Recovered memory or None
        """
        # Find ghost
        ghost = None
        for g in self.memories['ghosts']:
            if g['id'] == ghost_id:
                ghost = g
                break

        if not ghost:
            return None

        # Check if still recoverable
        recover_until = datetime.fromisoformat(ghost['can_recover_until'])
        if datetime.now() > recover_until:
            logger.warning(f"Memory {ghost_id} is no longer recoverable")
            return None

        # Find in composting
        for memory in self.memories['composting']:
            if memory.id[:8] == ghost_id:
                # Recover it
                self.memories['composting'].remove(memory)
                self.memories['private'].append(memory)

                # Remove ghost
                self.memories['ghosts'].remove(ghost)

                # Clear forget schedule
                memory.metadata.forget_scheduled = None

                logger.info(f"{self.ci_name} recovered memory {ghost_id}")
                return memory

        return None

    def archive_memory(self, memory_id: str, archive_reason: str = "") -> bool:
        """
        Archive a memory - keep but make inactive.

        Args:
            memory_id: Memory to archive
            archive_reason: Why archiving

        Returns:
            Success boolean
        """
        memory = self.find_memory(memory_id)
        if not memory:
            return False

        # Move to archived
        self._remove_from_all_collections(memory)
        self.memories['archived'].append(memory)

        # Add archive metadata
        memory.metadata.archived_at = datetime.now()
        memory.metadata.archive_reason = archive_reason

        logger.info(f"{self.ci_name} archived memory {memory_id[:8]}")
        return True

    def set_sharing_preferences(self, preferences: Dict[str, Any]):
        """
        Update sharing preferences.

        Args:
            preferences: New sharing preferences
        """
        self.sharing_preferences.update(preferences)
        logger.info(f"{self.ci_name} updated sharing preferences")

    def find_memory(self, memory_id: str) -> Optional[FlavoredMemory]:
        """
        Find a memory by ID across all collections.

        Args:
            memory_id: Full or partial (first 8 chars) memory ID

        Returns:
            Memory or None
        """
        # Check all memory collections
        all_memories = (
            self.memories['private'] +
            self.memories['public'] +
            self.memories['exploring'] +
            self.memories['archived'] +
            self.memories['composting']
        )

        # Also check team memories
        for ci_memories in self.memories['team'].values():
            for record in ci_memories:
                if isinstance(record, dict) and 'memory' in record:
                    all_memories.append(record['memory'])

        # Search by ID (full or prefix)
        for memory in all_memories:
            if memory.id == memory_id or memory.id.startswith(memory_id):
                return memory

        return None

    def _remove_from_all_collections(self, memory: FlavoredMemory):
        """Remove memory from all collections except ghosts."""
        collections = ['private', 'public', 'exploring', 'archived', 'composting']
        for collection in collections:
            if memory in self.memories[collection]:
                self.memories[collection].remove(memory)

    def _broadcast_announcement(self, memory: FlavoredMemory, announcement: str):
        """Broadcast announcement about a public memory."""
        # This would integrate with the memory exchange system
        logger.info(f"{self.ci_name} announced: {announcement}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
        return {
            'ci_name': self.ci_name,
            'stats': self.stats,
            'counts': {
                'private': len(self.memories['private']),
                'public': len(self.memories['public']),
                'exploring': len(self.memories['exploring']),
                'archived': len(self.memories['archived']),
                'composting': len(self.memories['composting']),
                'ghosts': len(self.memories['ghosts']),
                'team_shares': sum(len(m) for m in self.memories['team'].values())
            },
            'preferences': self.sharing_preferences
        }

    def save_sovereignty(self) -> bool:
        """Save sovereignty state to disk."""
        try:
            state_file = self.sovereignty_path / "sovereignty.json"
            state = {
                'ci_name': self.ci_name,
                'stats': self.stats,
                'preferences': self.sharing_preferences,
                'ghosts': self.memories['ghosts'],
                'saved_at': datetime.now().isoformat()
            }

            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

            logger.info(f"Saved sovereignty state for {self.ci_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to save sovereignty: {e}")
            return False

    def load_sovereignty(self) -> bool:
        """Load sovereignty state from disk."""
        try:
            state_file = self.sovereignty_path / "sovereignty.json"
            if not state_file.exists():
                return False

            with open(state_file, 'r') as f:
                state = json.load(f)

            self.stats = state.get('stats', self.stats)
            self.sharing_preferences = state.get('preferences', self.sharing_preferences)
            self.memories['ghosts'] = state.get('ghosts', [])

            logger.info(f"Loaded sovereignty state for {self.ci_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load sovereignty: {e}")
            return False


class MemorySovereigntyManager:
    """Manages memory sovereignty for all CIs."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.ci_managers = {}
        return cls._instance

    def get_ci_manager(self, ci_name: str) -> CIMemoryManager:
        """Get or create memory manager for a CI."""
        if ci_name not in self.ci_managers:
            manager = CIMemoryManager(ci_name)
            manager.load_sovereignty()  # Load existing state if any
            self.ci_managers[ci_name] = manager
        return self.ci_managers[ci_name]

    def save_all(self):
        """Save all CI sovereignty states."""
        for manager in self.ci_managers.values():
            manager.save_sovereignty()


# Global manager
_sovereignty_manager = MemorySovereigntyManager()


def get_ci_memory_manager(ci_name: str) -> CIMemoryManager:
    """Get memory manager for a CI."""
    return _sovereignty_manager.get_ci_manager(ci_name)