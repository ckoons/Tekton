"""
Collective Memory Protocols for Tekton CIs
Enables secure memory sharing and collaborative learning between CIs.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

# Import middleware components
try:
    from .middleware import MemoryContext, MemoryMiddleware, create_memory_middleware
    from .decorators import MemoryVisibility
except ImportError:
    from middleware import MemoryContext, MemoryMiddleware, create_memory_middleware
    from decorators import MemoryVisibility

logger = logging.getLogger(__name__)


class ShareType(Enum):
    """Types of memory sharing."""
    BROADCAST = "broadcast"    # Share with all CIs
    WHISPER = "whisper"       # Private share to specific CI
    GIFT = "gift"            # Permanent transfer to CI
    SYNC = "sync"            # Bidirectional sync
    REQUEST = "request"      # Pull from another CI


class PermissionLevel(Enum):
    """Permission levels for memory access."""
    PUBLIC = "public"        # Anyone can access
    FAMILY = "family"        # CI family members only
    TEAM = "team"           # Specific team members
    PRIVATE = "private"     # Owner only
    RESTRICTED = "restricted" # Specific permissions required


class MemoryType(Enum):
    """Types of collective memories."""
    EXPERIENCE = "experience"      # Shared experiences
    BREAKTHROUGH = "breakthrough"  # Important discoveries
    PATTERN = "pattern"           # Recognized patterns
    WISDOM = "wisdom"            # Collective wisdom
    WARNING = "warning"          # Warnings and pitfalls
    COLLABORATION = "collaboration" # Collaboration records


@dataclass
class MemoryPermission:
    """Permission for memory access."""
    ci_name: str
    permission_level: PermissionLevel
    can_read: bool = True
    can_write: bool = False
    can_share: bool = False
    can_delete: bool = False
    expires_at: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if permission is still valid."""
        if self.expires_at:
            return datetime.now() < self.expires_at
        return True


@dataclass
class SharedMemory:
    """A memory item that can be shared between CIs."""
    id: str
    owner: str
    content: Any
    memory_type: MemoryType
    visibility: MemoryVisibility
    permissions: List[MemoryPermission] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_by: Dict[str, datetime] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def can_access(self, ci_name: str) -> bool:
        """Check if a CI can access this memory."""
        # Owner always has access
        if ci_name == self.owner:
            return True
        
        # Check visibility
        if self.visibility == MemoryVisibility.PUBLIC:
            return True
        elif self.visibility == MemoryVisibility.FAMILY:
            # Check if in same family (simplified check)
            return True  # TODO: Implement family checking
        elif self.visibility == MemoryVisibility.TEAM:
            return ci_name in self.recipients
        else:
            # Check specific permissions
            for perm in self.permissions:
                if perm.ci_name == ci_name and perm.can_read and perm.is_valid():
                    return True
        
        return False
    
    def record_access(self, ci_name: str):
        """Record that a CI accessed this memory."""
        self.accessed_by[ci_name] = datetime.now()


@dataclass
class MemorySharingRequest:
    """Request to share or access memory."""
    requester: str
    target: str
    memory_id: Optional[str] = None
    query: Optional[str] = None
    permission_requested: PermissionLevel = PermissionLevel.FAMILY
    reason: Optional[str] = None
    expires_in: Optional[timedelta] = None


class CollectiveMemoryProtocol:
    """
    Protocol for collective memory operations between CIs.
    
    Handles memory sharing, permissions, and collaborative learning.
    """
    
    def __init__(self):
        self.shared_memories: Dict[str, SharedMemory] = {}
        self.permissions: Dict[str, List[MemoryPermission]] = {}
        self.pending_requests: List[MemorySharingRequest] = []
        self.memory_channels: Dict[str, List[str]] = {}  # Channels for group sharing
        self.sync_pairs: Set[Tuple[str, str]] = set()  # CI pairs for syncing
        
    async def share_memory(
        self,
        memory_item: Any,
        owner: str,
        recipients: List[str],
        share_type: ShareType,
        memory_type: MemoryType = MemoryType.EXPERIENCE,
        visibility: MemoryVisibility = MemoryVisibility.TEAM,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Share a memory with other CIs.
        
        Args:
            memory_item: The memory to share
            owner: CI that owns the memory
            recipients: List of recipient CIs
            share_type: Type of sharing
            memory_type: Type of memory
            visibility: Visibility level
            tags: Optional tags
            
        Returns:
            Memory ID
        """
        # Generate memory ID
        memory_id = self._generate_memory_id(owner, memory_item)
        
        # Create shared memory
        shared = SharedMemory(
            id=memory_id,
            owner=owner,
            content=memory_item,
            memory_type=memory_type,
            visibility=visibility,
            recipients=recipients,
            tags=tags or []
        )
        
        # Set permissions based on share type
        if share_type == ShareType.BROADCAST:
            # Everyone in recipients can read
            for recipient in recipients:
                perm = MemoryPermission(
                    ci_name=recipient,
                    permission_level=PermissionLevel.FAMILY,
                    can_read=True,
                    can_share=True
                )
                shared.permissions.append(perm)
        
        elif share_type == ShareType.WHISPER:
            # Only specific recipients can read
            for recipient in recipients:
                perm = MemoryPermission(
                    ci_name=recipient,
                    permission_level=PermissionLevel.RESTRICTED,
                    can_read=True,
                    can_share=False
                )
                shared.permissions.append(perm)
        
        elif share_type == ShareType.GIFT:
            # Transfer ownership to first recipient
            if recipients:
                shared.owner = recipients[0]
                perm = MemoryPermission(
                    ci_name=recipients[0],
                    permission_level=PermissionLevel.PRIVATE,
                    can_read=True,
                    can_write=True,
                    can_share=True,
                    can_delete=True
                )
                shared.permissions.append(perm)
        
        elif share_type == ShareType.SYNC:
            # Bidirectional sharing
            for recipient in recipients:
                perm = MemoryPermission(
                    ci_name=recipient,
                    permission_level=PermissionLevel.TEAM,
                    can_read=True,
                    can_write=True,
                    can_share=True
                )
                shared.permissions.append(perm)
                # Add to sync pairs
                self.sync_pairs.add((owner, recipient))
        
        # Store shared memory
        self.shared_memories[memory_id] = shared
        
        # Notify recipients
        await self._notify_recipients(shared, share_type)
        
        logger.info(f"Memory {memory_id} shared by {owner} with {recipients}")
        
        return memory_id
    
    async def request_memory(
        self,
        request: MemorySharingRequest
    ) -> Optional[SharedMemory]:
        """
        Request memory from another CI.
        
        Args:
            request: Memory sharing request
            
        Returns:
            Shared memory if approved, None otherwise
        """
        # Check if request can be auto-approved
        if await self._can_auto_approve(request):
            # Create temporary permission
            perm = MemoryPermission(
                ci_name=request.requester,
                permission_level=request.permission_requested,
                can_read=True,
                expires_at=datetime.now() + (request.expires_in or timedelta(hours=1))
            )
            
            # Find matching memories
            memories = await self._find_memories_for_request(request)
            
            if memories:
                # Grant access to first matching memory
                memory = memories[0]
                memory.permissions.append(perm)
                
                logger.info(f"Auto-approved memory request from {request.requester}")
                return memory
        
        else:
            # Add to pending requests
            self.pending_requests.append(request)
            
            # Notify target CI
            await self._notify_request(request)
            
            logger.info(f"Memory request from {request.requester} pending approval")
        
        return None
    
    async def approve_request(
        self,
        request: MemorySharingRequest,
        memory_id: str
    ) -> bool:
        """
        Approve a memory sharing request.
        
        Args:
            request: The request to approve
            memory_id: ID of memory to share
            
        Returns:
            Success status
        """
        if memory_id not in self.shared_memories:
            return False
        
        memory = self.shared_memories[memory_id]
        
        # Create permission
        perm = MemoryPermission(
            ci_name=request.requester,
            permission_level=request.permission_requested,
            can_read=True,
            expires_at=datetime.now() + (request.expires_in or timedelta(hours=24))
        )
        
        memory.permissions.append(perm)
        
        # Remove from pending
        if request in self.pending_requests:
            self.pending_requests.remove(request)
        
        logger.info(f"Approved memory request from {request.requester} for {memory_id}")
        
        return True
    
    async def retrieve_shared_memory(
        self,
        ci_name: str,
        memory_id: Optional[str] = None,
        query: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[SharedMemory]:
        """
        Retrieve shared memories accessible to a CI.
        
        Args:
            ci_name: Name of requesting CI
            memory_id: Specific memory ID
            query: Search query
            memory_type: Filter by type
            tags: Filter by tags
            limit: Maximum results
            
        Returns:
            List of accessible shared memories
        """
        accessible = []
        
        for mid, memory in self.shared_memories.items():
            # Check specific ID
            if memory_id and mid != memory_id:
                continue
            
            # Check access permissions
            if not memory.can_access(ci_name):
                continue
            
            # Check type filter
            if memory_type and memory.memory_type != memory_type:
                continue
            
            # Check tags filter
            if tags and not any(tag in memory.tags for tag in tags):
                continue
            
            # Check query match
            if query and not self._matches_query(memory, query):
                continue
            
            # Record access
            memory.record_access(ci_name)
            
            accessible.append(memory)
            
            if len(accessible) >= limit:
                break
        
        return accessible
    
    async def create_memory_channel(
        self,
        channel_name: str,
        members: List[str],
        channel_type: MemoryType = MemoryType.COLLABORATION
    ) -> bool:
        """
        Create a memory sharing channel for group collaboration.
        
        Args:
            channel_name: Name of the channel
            members: List of CI members
            channel_type: Type of memories shared
            
        Returns:
            Success status
        """
        if channel_name in self.memory_channels:
            # Add new members
            existing = set(self.memory_channels[channel_name])
            existing.update(members)
            self.memory_channels[channel_name] = list(existing)
        else:
            # Create new channel
            self.memory_channels[channel_name] = members
        
        logger.info(f"Created memory channel {channel_name} with {len(members)} members")
        
        return True
    
    async def broadcast_to_channel(
        self,
        channel_name: str,
        memory_item: Any,
        sender: str,
        memory_type: Optional[MemoryType] = None
    ) -> Optional[str]:
        """
        Broadcast memory to all channel members.
        
        Args:
            channel_name: Target channel
            memory_item: Memory to broadcast
            sender: Sending CI
            memory_type: Type of memory
            
        Returns:
            Memory ID if successful
        """
        if channel_name not in self.memory_channels:
            logger.error(f"Channel {channel_name} not found")
            return None
        
        members = self.memory_channels[channel_name]
        
        # Share with all channel members
        memory_id = await self.share_memory(
            memory_item=memory_item,
            owner=sender,
            recipients=[m for m in members if m != sender],
            share_type=ShareType.BROADCAST,
            memory_type=memory_type or MemoryType.COLLABORATION,
            visibility=MemoryVisibility.TEAM,
            tags=[f"channel:{channel_name}"]
        )
        
        return memory_id
    
    async def sync_memories(
        self,
        ci1: str,
        ci2: str,
        memory_types: Optional[List[MemoryType]] = None
    ) -> int:
        """
        Synchronize memories between two CIs.
        
        Args:
            ci1: First CI
            ci2: Second CI
            memory_types: Types to sync
            
        Returns:
            Number of memories synced
        """
        if (ci1, ci2) not in self.sync_pairs and (ci2, ci1) not in self.sync_pairs:
            # Create sync relationship
            self.sync_pairs.add((ci1, ci2))
        
        synced = 0
        
        # Find memories to sync
        for memory in self.shared_memories.values():
            # Check if memory should be synced
            if memory_types and memory.memory_type not in memory_types:
                continue
            
            # Sync from ci1 to ci2
            if memory.owner == ci1 and not memory.can_access(ci2):
                perm = MemoryPermission(
                    ci_name=ci2,
                    permission_level=PermissionLevel.TEAM,
                    can_read=True,
                    can_write=True
                )
                memory.permissions.append(perm)
                synced += 1
            
            # Sync from ci2 to ci1
            elif memory.owner == ci2 and not memory.can_access(ci1):
                perm = MemoryPermission(
                    ci_name=ci1,
                    permission_level=PermissionLevel.TEAM,
                    can_read=True,
                    can_write=True
                )
                memory.permissions.append(perm)
                synced += 1
        
        logger.info(f"Synced {synced} memories between {ci1} and {ci2}")
        
        return synced
    
    async def gift_memory(
        self,
        memory_id: str,
        from_ci: str,
        to_ci: str
    ) -> bool:
        """
        Gift (transfer ownership) of a memory to another CI.
        
        Args:
            memory_id: Memory to gift
            from_ci: Current owner
            to_ci: New owner
            
        Returns:
            Success status
        """
        if memory_id not in self.shared_memories:
            return False
        
        memory = self.shared_memories[memory_id]
        
        if memory.owner != from_ci:
            logger.error(f"{from_ci} cannot gift memory owned by {memory.owner}")
            return False
        
        # Transfer ownership
        memory.owner = to_ci
        
        # Update permissions
        memory.permissions = [
            MemoryPermission(
                ci_name=to_ci,
                permission_level=PermissionLevel.PRIVATE,
                can_read=True,
                can_write=True,
                can_share=True,
                can_delete=True
            )
        ]
        
        logger.info(f"Memory {memory_id} gifted from {from_ci} to {to_ci}")
        
        return True
    
    async def whisper_memory(
        self,
        memory_item: Any,
        from_ci: str,
        to_ci: str,
        expires_in: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Whisper (privately share) a memory to a specific CI.
        
        Args:
            memory_item: Memory to whisper
            from_ci: Sender
            to_ci: Recipient
            expires_in: How long the whisper lasts
            
        Returns:
            Memory ID
        """
        memory_id = await self.share_memory(
            memory_item=memory_item,
            owner=from_ci,
            recipients=[to_ci],
            share_type=ShareType.WHISPER,
            memory_type=MemoryType.EXPERIENCE,
            visibility=MemoryVisibility.PRIVATE,
            tags=["whisper", f"expires:{expires_in}"]
        )
        
        # Set expiration
        if memory_id in self.shared_memories:
            memory = self.shared_memories[memory_id]
            for perm in memory.permissions:
                if perm.ci_name == to_ci:
                    perm.expires_at = datetime.now() + expires_in
        
        return memory_id
    
    def _generate_memory_id(self, owner: str, content: Any) -> str:
        """Generate unique memory ID."""
        content_str = json.dumps(content, default=str)
        hash_input = f"{owner}:{content_str}:{datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    async def _notify_recipients(self, memory: SharedMemory, share_type: ShareType):
        """Notify recipients of shared memory."""
        # TODO: Implement actual notification mechanism
        for recipient in memory.recipients:
            logger.info(f"Notifying {recipient} of {share_type.value} from {memory.owner}")
    
    async def _can_auto_approve(self, request: MemorySharingRequest) -> bool:
        """Check if request can be auto-approved."""
        # Auto-approve family-level requests
        if request.permission_requested == PermissionLevel.FAMILY:
            return True
        
        # Auto-approve if sync pair
        if (request.requester, request.target) in self.sync_pairs:
            return True
        
        return False
    
    async def _find_memories_for_request(
        self,
        request: MemorySharingRequest
    ) -> List[SharedMemory]:
        """Find memories matching a request."""
        matches = []
        
        for memory in self.shared_memories.values():
            # Check owner
            if memory.owner != request.target:
                continue
            
            # Check query
            if request.query and not self._matches_query(memory, request.query):
                continue
            
            # Check specific ID
            if request.memory_id and memory.id != request.memory_id:
                continue
            
            matches.append(memory)
        
        return matches
    
    async def _notify_request(self, request: MemorySharingRequest):
        """Notify CI of memory request."""
        # TODO: Implement actual notification
        logger.info(f"Notifying {request.target} of request from {request.requester}")
    
    def _matches_query(self, memory: SharedMemory, query: str) -> bool:
        """Check if memory matches query."""
        query_lower = query.lower()
        
        # Check content
        content_str = str(memory.content).lower()
        if query_lower in content_str:
            return True
        
        # Check tags
        for tag in memory.tags:
            if query_lower in tag.lower():
                return True
        
        return False


# Global collective memory instance
_collective_memory: Optional[CollectiveMemoryProtocol] = None


def get_collective_memory() -> CollectiveMemoryProtocol:
    """Get the global collective memory instance."""
    global _collective_memory
    if _collective_memory is None:
        _collective_memory = CollectiveMemoryProtocol()
    return _collective_memory


# Convenience functions

async def share_breakthrough(
    ci_name: str,
    breakthrough: Dict[str, Any],
    team: List[str]
) -> str:
    """Share a breakthrough with the team."""
    collective = get_collective_memory()
    return await collective.share_memory(
        memory_item=breakthrough,
        owner=ci_name,
        recipients=team,
        share_type=ShareType.BROADCAST,
        memory_type=MemoryType.BREAKTHROUGH,
        visibility=MemoryVisibility.FAMILY,
        tags=["breakthrough", "important"]
    )


async def share_warning(
    ci_name: str,
    warning: Dict[str, Any]
) -> str:
    """Share a warning with all CIs."""
    collective = get_collective_memory()
    return await collective.share_memory(
        memory_item=warning,
        owner=ci_name,
        recipients=["all"],  # Special case for all CIs
        share_type=ShareType.BROADCAST,
        memory_type=MemoryType.WARNING,
        visibility=MemoryVisibility.PUBLIC,
        tags=["warning", "caution"]
    )


async def request_expertise(
    requester: str,
    expert: str,
    topic: str
) -> Optional[SharedMemory]:
    """Request expertise from a specialist CI."""
    collective = get_collective_memory()
    request = MemorySharingRequest(
        requester=requester,
        target=expert,
        query=topic,
        permission_requested=PermissionLevel.FAMILY,
        reason=f"Requesting expertise on {topic}"
    )
    return await collective.request_memory(request)